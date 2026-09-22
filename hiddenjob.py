#!/usr/bin/env python3
"""A private, configuration-first job discovery and review ledger.

The program finds less-visible postings from publisher-declared sitemaps and
records source evidence. Its optional ATS adapter can prefill a reviewed form;
submission, email, account creation, and complaint filing remain deliberate
human actions guarded by explicit flags.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

UA = "Hiddenjob/0.1 (research-and-review)"
PERM_MARKERS = [
    (r"\bforeign\s+equivalent\b", 3),
    (r"\bin the job offered\b", 3),
    (r"\b(?:mail|send)\s+(?:your\s+)?resumes?\b", 3),
    (r"\bnotice of filing\b|\blabor certification\b", 3),
    (r"\bminimum requirements?\b|\bjob duties\b|\bspecial (?:skill )?requirements?\b", 2),
    (r"\btelecommut|\bprogressively responsible\b|\bPERM\b", 2),
]
LCA_MARKERS = [
    (r"\blabor condition application\b", 3),
    (r"\bH-?1B\b|\bnon-?immigrant worker\b|\bSOC code\b|\bwage level\b", 2),
    (r"\bperiod of employment\b|\bpublic access file\b", 1),
]


class FetchBlocked(RuntimeError):
    """A source cannot be measured; it must not be treated as an empty result."""


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def clean_text(raw: str) -> str:
    raw = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def classify(text: str) -> dict[str, object]:
    """Classify wording, not legal status or employer intent."""
    def score(markers: list[tuple[str, int]]) -> tuple[int, list[str]]:
        hits = [pattern for pattern, _ in markers if re.search(pattern, text, re.I)]
        return sum(weight for pattern, weight in markers if pattern in hits), hits

    perm, perm_hits = score(PERM_MARKERS)
    lca, lca_hits = score(LCA_MARKERS)
    if perm >= 5:
        kind = "perm-like"
    elif lca >= 6:
        kind = "lca-like"
    elif re.search(r"equally or better qualified U\.?S\.? worker|H-?1B dependent", text, re.I):
        kind = "recruitment-notice-like"
    else:
        kind = "unclassified"
    return {"classification": kind, "perm_score": perm, "lca_score": lca,
            "marker_hits": perm_hits + lca_hits}


def is_challenge_page(lower_body: str) -> bool:
    """Identify bot-wall signatures without rejecting ordinary job-page wording."""
    return ("just a moment" in lower_body or "challenge-platform" in lower_body or
            "cf-chl-" in lower_body or ("hcaptcha" in lower_body and "challenge" in lower_body))


def fetch(url: str, timeout: int = 25) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", "replace")
            status, final_url = response.status, response.geturl()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return "", url
        raise FetchBlocked(f"{url}: HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchBlocked(f"{url}: {exc}") from exc
    lower = body[:8000].lower()
    # Do not treat ordinary page text mentioning CAPTCHA as a block. Detect the
    # known interstitial signatures instead.
    if status != 200 or not body.strip() or is_challenge_page(lower):
        raise FetchBlocked(f"{url}: unmeasurable response (HTTP {status}, {len(body)} bytes)")
    return body, final_url


def robots_sitemaps(robots_url: str, fallback: str) -> list[str]:
    text, _ = fetch(robots_url)
    found = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)
    return found or [fallback]


def sitemap_entries(xml: str) -> tuple[list[str], list[str]]:
    """Return child sitemap URLs and leaf URLs. Namespace-agnostic by design."""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise FetchBlocked(f"invalid sitemap XML: {exc}") from exc
    tag = root.tag.rsplit("}", 1)[-1]
    locs = [node.text.strip() for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "loc" and node.text]
    return (locs, []) if tag == "sitemapindex" else ([], locs)


def walk_sitemaps(seeds: list[str], max_urls: int = 5000) -> tuple[list[str], list[str]]:
    queue, seen, urls, blocked = list(seeds), set(), [], []
    while queue and len(urls) < max_urls:
        sitemap = queue.pop(0)
        if sitemap in seen:
            continue
        seen.add(sitemap)
        try:
            body, _ = fetch(sitemap)
            children, leaves = sitemap_entries(body)
        except FetchBlocked as exc:
            blocked.append(str(exc))
            continue
        # Career/job child maps are a smaller, more relevant denominator first.
        career_children = [u for u in children if re.search(r"job|career|position|opening", urllib.parse.urlparse(u).path, re.I)]
        queue.extend(career_children or children)
        urls.extend(leaves)
    return urls[:max_urls], blocked


def jsonld_job(raw: str) -> dict[str, object]:
    for block in re.findall(r"<script[^>]+(?:application/ld\+json|ld\+json)[^>]*>(.*?)</script>", raw, re.I | re.S):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        items = parsed if isinstance(parsed, list) else parsed.get("@graph", [parsed]) if isinstance(parsed, dict) else []
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
    return {}


def extract_job(url: str, raw: str, source: str) -> dict[str, object]:
    item = jsonld_job(raw)
    description = clean_text(str(item.get("description") or raw))
    organization = item.get("hiringOrganization")
    company = organization.get("name", "") if isinstance(organization, dict) else ""
    title = str(item.get("title") or "")
    if not title:
        match = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.I | re.S)
        title = clean_text(match.group(1)) if match else "Untitled posting"
    return {
        "url": url,
        "source": source,
        "title": title[:300],
        "company": str(company)[:300],
        "date_posted": str(item.get("datePosted") or ""),
        "description": description,
        "description_sha256": hashlib.sha256(description.encode()).hexdigest(),
        **classify(description),
    }


def config_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_config(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"Config not found: {path}. Copy config/targets.example.json to config/targets.json first.")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data.get("sources"), list):
        raise SystemExit("Config must contain a sources list.")
    return data


def data_root(cfg: dict[str, object], cfg_path: Path) -> Path:
    root = Path(str(cfg.get("data_dir", ".hiddenjob")))
    root = root if root.is_absolute() else cfg_path.parent.parent / root
    root.mkdir(parents=True, exist_ok=True)
    (root / "evidence").mkdir(exist_ok=True)
    return root


def database(root: Path) -> sqlite3.Connection:
    con = sqlite3.connect(root / "hiddenjob.sqlite3")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
      url TEXT PRIMARY KEY, source TEXT NOT NULL, title TEXT, company TEXT, date_posted TEXT,
      classification TEXT, perm_score INTEGER, lca_score INTEGER, marker_hits TEXT,
      description_sha256 TEXT, evidence_path TEXT, live INTEGER NOT NULL DEFAULT 1, last_checked TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS applications (
      job_url TEXT PRIMARY KEY REFERENCES jobs(url), state TEXT NOT NULL, note TEXT, updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS complaints (
      id INTEGER PRIMARY KEY, agency TEXT NOT NULL CHECK(agency IN ('eeoc','ofccp')),
      employer TEXT NOT NULL, contractor_status TEXT NOT NULL CHECK(contractor_status IN ('unknown','reported','verified')),
      alleged_date TEXT NOT NULL, state TEXT NOT NULL, note TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS complaint_evidence (
      complaint_id INTEGER NOT NULL REFERENCES complaints(id), job_url TEXT REFERENCES jobs(url),
      source_url TEXT NOT NULL, captured_at TEXT NOT NULL, sha256 TEXT NOT NULL, evidence_path TEXT NOT NULL
    );
    """)
    return con


def save_evidence(root: Path, url: str, content: str) -> Path:
    digest = hashlib.sha256(content.encode()).hexdigest()
    path = root / "evidence" / f"{digest}.html"
    if not path.exists():
        path.write_text(content)
    return path


def cmd_init(args: argparse.Namespace) -> int:
    destination = config_path(args.config)
    if destination.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite {destination}; pass --force to replace it.")
    example = Path(__file__).parent / "config" / "targets.example.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(example.read_text())
    print(f"Created {destination}. Review it before running a sync.")
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    cfg_path = config_path(args.config)
    cfg, root = load_config(cfg_path), None
    root = data_root(cfg, cfg_path)
    con = database(root)
    for source in cfg["sources"]:
        if not isinstance(source, dict) or not all(k in source for k in ("name", "robots_url", "sitemap_fallback", "job_url_pattern")):
            raise SystemExit("Every source needs name, robots_url, sitemap_fallback, and job_url_pattern.")
        name = str(source["name"])
        try:
            seeds = robots_sitemaps(str(source["robots_url"]), str(source["sitemap_fallback"]))
            urls, blocked = walk_sitemaps(seeds, args.max_sitemap_urls)
        except FetchBlocked as exc:
            print(f"{name}: blocked; inventory unchanged: {exc}", file=sys.stderr)
            continue
        candidate_re = source.get("job_url_regex")
        candidates = [u for u in urls if str(source["job_url_pattern"]) in urllib.parse.urlparse(u).path and
                      (not candidate_re or re.search(str(candidate_re), urllib.parse.urlparse(u).path))]
        if not candidates:
            print(f"{name}: no matching job URLs; not treating this as a negative finding.", file=sys.stderr)
        if blocked:
            print(f"{name}: {len(blocked)} sitemap(s) could not be measured; preserving existing rows.", file=sys.stderr)
        fetched = 0
        for url in candidates[:args.limit]:
            try:
                raw, final_url = fetch(url)
            except FetchBlocked as exc:
                print(f"skip: {exc}", file=sys.stderr)
                continue
            record = extract_job(final_url, raw, name)
            evidence = save_evidence(root, final_url, raw)
            con.execute("""INSERT INTO jobs(url,source,title,company,date_posted,classification,perm_score,lca_score,marker_hits,description_sha256,evidence_path,live,last_checked)
              VALUES(:url,:source,:title,:company,:date_posted,:classification,:perm_score,:lca_score,:marker_hits,:description_sha256,:evidence_path,1,:last_checked)
              ON CONFLICT(url) DO UPDATE SET source=excluded.source,title=excluded.title,company=excluded.company,date_posted=excluded.date_posted,classification=excluded.classification,perm_score=excluded.perm_score,lca_score=excluded.lca_score,marker_hits=excluded.marker_hits,description_sha256=excluded.description_sha256,evidence_path=excluded.evidence_path,live=1,last_checked=excluded.last_checked""",
              {**record, "marker_hits": json.dumps(record["marker_hits"]), "evidence_path": str(evidence), "last_checked": now()})
            fetched += 1
        con.commit()
        print(f"{name}: declared URLs={len(urls)}, candidates={len(candidates)}, captured={fetched}, blocked_maps={len(blocked)}")
    return 0


def rows(con: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict[str, object]]:
    return [dict(row) for row in con.execute(sql, params)]


def with_db(args: argparse.Namespace) -> tuple[sqlite3.Connection, Path]:
    cp = config_path(args.config)
    cfg = load_config(cp)
    root = data_root(cfg, cp)
    return database(root), root


def cmd_jobs(args: argparse.Namespace) -> int:
    con, _ = with_db(args)
    where, params = ["live=1"], []
    if args.classification:
        where.append("classification=?"); params.append(args.classification)
    if args.company:
        where.append("company LIKE ?"); params.append(f"%{args.company}%")
    data = rows(con, "SELECT url,company,title,classification,perm_score,lca_score,date_posted,last_checked FROM jobs WHERE " + " AND ".join(where) + " ORDER BY perm_score DESC,lca_score DESC,title LIMIT ?", tuple(params + [args.limit]))
    print(json.dumps(data, indent=2))
    return 0


def cmd_stage(args: argparse.Namespace) -> int:
    con, _ = with_db(args)
    exists = con.execute("SELECT 1 FROM jobs WHERE url=?", (args.url,)).fetchone()
    if not exists:
        raise SystemExit("That URL is not in the local evidence ledger. Sync and review the posting first.")
    con.execute("INSERT INTO applications(job_url,state,note,updated_at) VALUES(?,?,?,?) ON CONFLICT(job_url) DO UPDATE SET state=excluded.state,note=excluded.note,updated_at=excluded.updated_at", (args.url, "staged", args.note or "", now()))
    con.commit()
    print("Staged for human review. No application was submitted or sent.")
    return 0


def cmd_track(args: argparse.Namespace) -> int:
    allowed = {"staged", "drafted", "submitted", "interview", "offer", "rejected", "withdrawn", "closed"}
    if args.state not in allowed:
        raise SystemExit(f"state must be one of: {', '.join(sorted(allowed))}")
    con, _ = with_db(args)
    if not con.execute("SELECT 1 FROM applications WHERE job_url=?", (args.url,)).fetchone():
        raise SystemExit("Stage the job first so the record has a reviewed source posting.")
    con.execute("UPDATE applications SET state=?,note=?,updated_at=? WHERE job_url=?", (args.state, args.note or "", now(), args.url))
    con.commit(); print(f"Tracked {args.state}. Record whether you submitted only after an actual confirmation.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """Run the optional local browser adapter against a reviewed, staged job."""
    con, root = with_db(args)
    app = con.execute("SELECT state FROM applications WHERE job_url=?", (args.url,)).fetchone()
    if not app or app["state"] not in {"staged", "drafted"}:
        raise SystemExit("Stage and review the job before using the browser adapter.")
    profile = Path(args.profile).expanduser()
    if not profile.exists():
        raise SystemExit(f"Private profile not found: {profile}")
    if args.submit and not args.confirm_submit:
        raise SystemExit("Submitting also requires --confirm-submit; prefill is the default.")
    if args.submit and __import__("os").environ.get("HIDDENJOB_AUTOSUBMIT") != "1":
        raise SystemExit("Submitting also requires HIDDENJOB_AUTOSUBMIT=1 in this process environment.")
    folder = root / "applications" / hashlib.sha256(args.url.encode()).hexdigest()[:16]
    folder.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(Path(__file__).with_name("ats_prefill.py")), "--url", args.url,
           "--profile", str(profile), "--evidence-dir", str(folder)]
    if args.submit:
        cmd.append("--submit")
    if args.dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if result.returncode not in (0, 2):
        raise SystemExit(result.returncode)
    print(result.stdout, end="")
    result_path = folder / "prefill-result.json"
    if args.submit and result_path.exists():
        outcome = json.loads(result_path.read_text()).get("outcome")
        if outcome == "submitted":
            con.execute("UPDATE applications SET state='submitted', updated_at=? WHERE job_url=?", (now(), args.url))
            con.commit()
    return result.returncode


def cmd_apply_staged(args: argparse.Namespace) -> int:
    """Process a bounded batch that the person already staged and reviewed."""
    con, _ = with_db(args)
    sql = "SELECT a.job_url FROM applications a JOIN jobs j ON j.url=a.job_url WHERE a.state IN ('staged','drafted')"
    params: list[object] = []
    if args.classification:
        sql += " AND j.classification=?"; params.append(args.classification)
    jobs = rows(con, sql + " ORDER BY a.updated_at LIMIT ?", tuple(params + [args.limit]))
    if not jobs:
        print("No staged jobs match the requested batch.")
        return 0
    outcomes = []
    for row in jobs:
        per_job = argparse.Namespace(config=args.config, url=row["job_url"], profile=args.profile,
                                     submit=args.submit, confirm_submit=args.confirm_submit, dry_run=args.dry_run)
        try:
            code = cmd_apply(per_job)
        except SystemExit as exc:
            code = int(exc.code) if isinstance(exc.code, int) else 1
        outcomes.append({"url": row["job_url"], "exit_code": code})
    print(json.dumps({"processed": len(outcomes), "outcomes": outcomes}, indent=2))
    return 0 if all(x["exit_code"] == 0 for x in outcomes) else 2


def complaint_guidance(agency: str, alleged: date) -> dict[str, object]:
    elapsed = (date.today() - alleged).days
    if agency == "ofccp":
        return {"agency": "DOL OFCCP", "deadline": "300 calendar days from the alleged action", "days_elapsed": elapsed,
                "route": "Pre-complaint inquiry or complaint: https://www.dol.gov/agencies/ofccp/contact/file-complaint",
                "scope": "Federal-contractor/subcontractor employment discrimination based on disability or protected-veteran status; agency fit is not determined by this tool."}
    return {"agency": "EEOC", "deadline": "Usually 180 days; often 300 days when an applicable state/local agency enforces a parallel law", "days_elapsed": elapsed,
            "route": "Public Portal and charge process: https://www.eeoc.gov/how-file-charge-employment-discrimination",
            "scope": "Protected-basis employment discrimination; federal-contractor status alone does not establish an EEOC claim."}


def cmd_complaint_create(args: argparse.Namespace) -> int:
    try:
        alleged = date.fromisoformat(args.alleged_date)
    except ValueError as exc:
        raise SystemExit("--alleged-date must be YYYY-MM-DD") from exc
    con, _ = with_db(args)
    stamp = now()
    cur = con.execute("INSERT INTO complaints(agency,employer,contractor_status,alleged_date,state,note,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (args.agency, args.employer, args.contractor_status, alleged.isoformat(), "draft", args.note or "", stamp, stamp))
    con.commit()
    out = {"case_id": cur.lastrowid, "filing_state": "draft", "not_filed": True, **complaint_guidance(args.agency, alleged)}
    print(json.dumps(out, indent=2))
    return 0


def cmd_complaint_evidence(args: argparse.Namespace) -> int:
    con, root = with_db(args)
    case = con.execute("SELECT id FROM complaints WHERE id=?", (args.case,)).fetchone()
    job = con.execute("SELECT url,evidence_path,description_sha256 FROM jobs WHERE url=?", (args.url,)).fetchone()
    if not case or not job:
        raise SystemExit("Case or job URL not found. Capture the posting through sync before attaching it.")
    con.execute("INSERT INTO complaint_evidence(complaint_id,job_url,source_url,captured_at,sha256,evidence_path) VALUES(?,?,?,?,?,?)", (args.case, args.url, args.url, now(), job["description_sha256"], job["evidence_path"]))
    con.commit(); print("Evidence linked to draft case. This does not file or transmit anything.")
    return 0


def cmd_complaint_list(args: argparse.Namespace) -> int:
    con, _ = with_db(args)
    print(json.dumps(rows(con, "SELECT id,agency,employer,contractor_status,alleged_date,state,created_at,updated_at FROM complaints ORDER BY id DESC"), indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    con, _ = with_db(args)
    out = {
        "jobs_by_classification": rows(con, "SELECT classification,count(*) AS count FROM jobs WHERE live=1 GROUP BY classification ORDER BY count DESC"),
        "application_states": rows(con, "SELECT state,count(*) AS count FROM applications GROUP BY state ORDER BY count DESC"),
        "complaint_cases": rows(con, "SELECT agency,state,count(*) AS count FROM complaints GROUP BY agency,state ORDER BY agency,state"),
        "notice": "Records are local. Complaint cases remain drafts until the person filing submits through the official agency process.",
    }
    print(json.dumps(out, indent=2)); return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", default="config/targets.json", help="private runtime config path")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--force", action="store_true"); init.set_defaults(func=cmd_init)
    sync = sub.add_parser("sync"); sync.add_argument("--limit", type=int, default=25); sync.add_argument("--max-sitemap-urls", type=int, default=5000); sync.set_defaults(func=cmd_sync)
    jobs = sub.add_parser("jobs"); jobs.add_argument("--classification"); jobs.add_argument("--company"); jobs.add_argument("--limit", type=int, default=50); jobs.set_defaults(func=cmd_jobs)
    stage = sub.add_parser("stage"); stage.add_argument("url"); stage.add_argument("--note"); stage.set_defaults(func=cmd_stage)
    track = sub.add_parser("track"); track.add_argument("url"); track.add_argument("state"); track.add_argument("--note"); track.set_defaults(func=cmd_track)
    apply = sub.add_parser("apply", help="optional browser prefill for a staged job")
    apply.add_argument("url"); apply.add_argument("--profile", default="config/profile.json")
    apply.add_argument("--submit", action="store_true", help="click submit only with the environment and confirmation gates")
    apply.add_argument("--confirm-submit", action="store_true", help="acknowledge that a real submission is requested")
    apply.add_argument("--dry-run", action="store_true", help="validate private profile and planned action without opening a browser")
    apply.set_defaults(func=cmd_apply)
    batch = sub.add_parser("apply-staged", help="bounded prefill batch for already-staged jobs")
    batch.add_argument("--profile", default="config/profile.json"); batch.add_argument("--classification")
    batch.add_argument("--limit", type=int, default=3); batch.add_argument("--submit", action="store_true")
    batch.add_argument("--confirm-submit", action="store_true"); batch.add_argument("--dry-run", action="store_true")
    batch.set_defaults(func=cmd_apply_staged)
    complaint = sub.add_parser("complaint"); csub = complaint.add_subparsers(dest="complaint_command", required=True)
    cc = csub.add_parser("create"); cc.add_argument("--agency", required=True, choices=("eeoc", "ofccp")); cc.add_argument("--employer", required=True); cc.add_argument("--alleged-date", required=True); cc.add_argument("--contractor-status", choices=("unknown", "reported", "verified"), default="unknown"); cc.add_argument("--note"); cc.set_defaults(func=cmd_complaint_create)
    ce = csub.add_parser("evidence"); ce.add_argument("--case", type=int, required=True); ce.add_argument("--url", required=True); ce.set_defaults(func=cmd_complaint_evidence)
    cl = csub.add_parser("list"); cl.set_defaults(func=cmd_complaint_list)
    report = sub.add_parser("report"); report.set_defaults(func=cmd_report)
    return p


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
