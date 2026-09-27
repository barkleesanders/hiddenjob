#!/usr/bin/env python3
"""Rank hiddenjob ledger postings against Barklee's profile with qualification gates.

Reads the SQLite ledger, scores each live posting on title/company/description
fit, hard-excludes Spanish-fluency-required roles, and prints a ranked shortlist
as JSON. Read-only: never mutates the ledger.

Qualification model (improved 2026-09-25):
- Location mentions alone NEVER make a posting actionable. A posting must match
  Barklee's role families in the TITLE (role_fit >= ROLE_FIT_MIN) to be actionable.
- Total score must clear ACTIONABLE_MIN.
- Seniority band: individual contributor, ~2-8 yrs. Hard-exclude C-suite/VP/
  Director/principal-architect and roles demanding 15+ yrs.
- Hard-exclude Spanish-fluency-required roles (Barklee is not fluent).
- Hard-exclude internships/unpaid roles and active-clearance-required roles.
- Watch tier: plausible-but-risky (relocation-only on-site, senior-leaning).
- Compliance-lead tier: perm-like / lca-like / recruitment-notice-like
  postings are the system's core discovery target — employers satisfy
  recruitment compliance through these low-visibility channels, so the
  notice is surfaced, never excluded. Resolve each to a live employer
  application before staging; never apply to the notice text itself.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

LEDGER = Path(__file__).parents[1] / "ledger" / "hiddenjob.sqlite3"
# allow override: hiddenjob_rank.py <path-to-sqlite3>
if len(sys.argv) > 1:
    LEDGER = Path(sys.argv[1])

# --- role-family title matches (points) ---
TITLE_POSITIVE = [
    (r"\bproduct manager\b", 30), (r"\btechnical product manager\b", 35),
    (r"\brotational product manager\b", 40), (r"\bassociate product manager\b", 30),
    (r"\bforward deployed\b", 30), (r"\bsolutions engineer\b", 28),
    (r"\bsales engineer\b", 24), (r"\btechnical account manager\b", 24),
    (r"\bcustomer success engineer\b", 22), (r"\bsupport engineer\b", 26),
    (r"\bit support\b", 24), (r"\bservice desk\b", 18), (r"\bdesktop support\b", 18),
    (r"\bsystems engineer\b", 26), (r"\bendpoint engineer\b", 26),
    (r"\bit administrator\b", 20), (r"\bimplementation engineer\b", 22),
    (r"\btechnical support\b", 20), (r"\bprogram manager\b", 18),
    (r"\bproduct operations\b", 18), (r"\bai\b.*\bengineer\b", 15),
    (r"\bllm\b", 12), (r"\bprompt engineer\b", 15),
    (r"\boperations (manager|specialist|associate|engineer)\b", 14),
    (r"\bsupport specialist\b", 22), (r"\bproduct support\b", 22),
    (r"\bhelp desk\b", 18), (r"\bdeployment specialist\b", 16),
    (r"\boperations engineer\b", 20), (r"\bdelivery engineer\b", 18),
    (r"\bcustomer support engineer\b", 20),
    (r"\bcustomer success manager\b", 16), (r"\baccount executive\b", -8),
]
TITLE_NEGATIVE = [
    (r"\bintern\b", -50), (r"\bjunior\b", -15), (r"\bstaff\b.*\barchitect\b", -10),
    (r"\bprincipal\b.*\barchitect\b", -10), (r"\bdistinguished\b", -25),
    (r"\bvp\b", -25), (r"\bdirector\b", -20), (r"\bchief\b", -30),
    (r"\bstaff\b.*\bsoftware\b", -20), (r"\bprincipal\b.*\bsoftware\b", -20),
]

# --- description-level qualification signals ---
SKILL_POSITIVE = [
    (r"\b(mdm|jamf|kandji|okta|azure ad|entra|active directory)\b", 8),
    (r"\b(zendesk|freshdesk|intercom|servicenow|jira)\b", 8),
    (r"\b(network(ing)?|tcp/ip|dns|dhcp|vpn|wi-?fi)\b", 8),
    (r"\b(mac\s?os|macos|windows|ios|android)\s+(support|admin|troubleshoot)", 6),
    (r"\b(saas|api|rest|webhook|sql)\b", 6),
    (r"\b(agile|scrum|kanban|roadmap|backlog|a/b test|experimentation)\b", 6),
    (r"\b(llm|genai|generative ai|prompt|rag|agents?)\b", 8),
    (r"\b(ai|machine learning)\s+(product|platform|assistant|ops|support)\b", 8),
    (r"\b(stakeholder|cross[- ]functional|go[- ]to[- ]market)\b", 4),
    (r"\b(onboard(ing)?|provision(ing)?|lifecycle)\b", 6),
]
SENIORITY_EXCLUDE = [
    r"\b(15|1[6-9]|20)\s*\+\s*years", r"\bfifteen\s+years",
    r"\b(principal|distinguished|fellow)\s+(engineer|architect|scientist|pm)\b",
    r"\bvp\b.{0,20}\b(product|engineering|sales|success)\b",
    r"\b(head|chief)\b.{0,20}\bof\b",
    # senior TPM band sits above Barklee's IC band (triaged 2026-09-26: OpenAI Senior TPM)
    r"\bsenior\b.{0,30}\btechnical program manager\b",
    r"\bsenior\b.{0,10}\btpm\b",
]
# Title-only hard excludes: student / new-grad pipelines. Scoped to the title
# because descriptions legitimately mention mentoring interns.
TITLE_HARD_EXCLUDE = [
    r"\bintern(ship)?\b", r"\bco-?op\b", r"\bapprentice(ship)?\b",
    r"\bnew[\s-]?grad\b", r"\brecent grad", r"\buniversity grad",
    r"\bcollege grad", r"\bclass of 20\d\d\b", r"\b20(2[6-9]|30)\s*start\b",
    r"\breturning intern\b",
]
# Europe/EMEA-locked postings. Applied to title + location fields only, never the
# full description (US postings legitimately mention European teams/customers).
EUROPE_LOCKED = [
    r"\beurope\b", r"\bemea\b", r"\buk\b", r"\bengland\b", r"\bireland\b",
    r"\bgermany\b", r"\bfrance\b", r"\bspain\b", r"\bitaly\b", r"\bnetherlands\b",
    r"\bsweden\b", r"\bswedish\b", r"\bnorway\b", r"\bdenmark\b", r"\bfinland\b",
    r"\bpoland\b", r"\bportugal\b", r"\bbelgium\b", r"\baustria\b", r"\bswitzerland\b",
    r"\baustralia\b", r"\bnew zealand\b",
]
# Visa-compliance notice classifications (perm-like, lca-like,
# recruitment-notice-like) are the system's core discovery target: employers use
# these low-visibility channels to satisfy recruitment compliance while the real
# role stays hard to find. They are SURFACED as their own tier, never excluded.
# Fit gates (Spanish, intern, seniority, location) still apply to the person;
# the notice classification only changes the tier, not the fit.
NOTICE_CLASSIFICATIONS = {"perm-like", "lca-like", "recruitment-notice-like"}
HARD_EXCLUDE = [
    # Spanish fluency (Barklee is not fluent — 2026-09-25)
    r"\bspanish\b.{0,60}\bfluent\b", r"\bfluent\b.{0,60}\bspanish\b",
    r"\bbilingual\b.{0,40}\bspanish\b", r"\bspanish\b.{0,40}\bbilingual\b",
    r"\bspanish\b.{0,30}\brequired\b", r"\bspanish\b.{0,30}\bspeaking\b",
    # internship / unpaid
    r"\bintern(ship)?\b.{0,30}\bunpaid\b", r"\bunpaid\b.{0,30}\bintern",
    r"\bthis is an unpaid\b",
    # active clearance (Barklee holds none on record)
    r"\bactive\s+(secret|top secret|ts/sci|security)\s+clearance\b",
    r"\bsecurity clearance.{0,20}required\b",
    r"\bsecret clearance\b.{0,40}\b(required|eligibility|eligible)\b",
    r"\beligibility\b.{0,40}\bsecret clearance\b",
]
WATCH_PATTERNS = [
    # specific non-US metro in the posting with no remote/US eligibility: downgrade
    (r"\b(london|dublin|berlin|toronto|sydney|singapore|tokyo|amsterdam|paris|madrid|vancouver)\b", "non-us-metro"),
    # on-site required outside his market: plausible only if remote/hybrid exists
    (r"\b(on[- ]site|in[- ]office)\b.{0,40}\b(new york|austin|seattle|boston|denver|chicago|los angeles|atlanta|washington,?\s*dc)\b", "onsite-outside-sf"),
    (r"\b(10|12)\s*\+\s*years", "senior-leaning"),
    (r"\bsenior\b.{0,30}\b(staff|principal)\b", "senior-leaning"),
    (r"\brelocation.{0,20}(required|assistance)\b", "relocation"),
]
LOCATION_POSITIVE = [r"\bremote\b", r"\bsan francisco\b", r"\bbay area\b", r"\bmenlo park\b",
                     r"\bunited states\b", r"\banywhere\b"]
LOCATION_NEGATIVE = [r"\b(london|berlin|toronto|dublin|sydney|singapore|tokyo)\b.{0,20}\bonly\b"]

ROLE_FIT_MIN = 18   # must match a role family in the title — location alone is not enough
ACTIONABLE_MIN = 20  # total score floor for the actionable tier

LOCATION_KEYS = {"location", "locationname", "addresslocality", "addressregion",
                 "addresscountry", "workplacetype", "workplace", "office", "offices"}

def extract_location_context(raw):
    """Pull location-ish fields out of an evidence JSON dict; empty string if none."""
    bits = []
    def walk(o, key=""):
        if isinstance(o, dict):
            for k, v in o.items():
                lk = str(k).lower()
                if any(tok in lk for tok in ("location", "address", "workplace", "office")):
                    bits.append(json.dumps(v)[:400])
                else:
                    walk(v, lk)
        elif isinstance(o, list):
            for v in o:
                walk(v, key)
    walk(raw)
    return " ".join(bits).lower()

def classify(title, company, description, loc_text="", classification=""):
    t = f"{title}".lower()
    d = f"{description or ''}".lower()[:8000]
    # normalize unicode hyphens/dashes so on-site / in-office patterns match
    d = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2212]", "-", d)
    text = f"{t} {d}"
    loc = f"{t} {loc_text}".lower()
    # Compliance-channel notice? Surfaces as its own tier below (after fit gates).
    is_notice = (classification or "").strip().lower() in NOTICE_CLASSIFICATIONS
    # Student / new-grad pipelines never fit, title-scoped.
    for pat in TITLE_HARD_EXCLUDE:
        if re.search(pat, t):
            return {"tier": "excluded", "score": 0, "role_fit": 0,
                    "reason": "student-or-newgrad-pipeline"}
    for pat in HARD_EXCLUDE:
        if re.search(pat, text):
            return {"tier": "excluded", "score": 0, "role_fit": 0, "reason": "hard-exclude"}
    for pat in SENIORITY_EXCLUDE:
        if re.search(pat, text):
            return {"tier": "excluded", "score": 0, "role_fit": 0, "reason": "seniority-out-of-band"}
    # Europe/EMEA-locked postings are out of band for a US applicant.
    for pat in EUROPE_LOCKED:
        if re.search(pat, loc):
            return {"tier": "excluded", "score": 0, "role_fit": 0, "reason": "location-europe-locked"}
    # Location eligibility: country-locked non-US postings are excluded.
    if re.search(r"\bremote\s*-\s*(india|south korea|korea|singapore|japan|australia|ireland|germany|uk)\b", loc) \
       or re.search(r"\bseoul\b.{0,20}south korea\b", loc) \
       or re.search(r"\b(london|dublin|berlin|toronto|sydney|singapore|tokyo|amsterdam|paris|madrid|vancouver|seoul)\b.{0,25}\b(united kingdom|ireland|germany|canada|australia|japan|france|spain|netherlands)\b", loc):
        return {"tier": "excluded", "score": 0, "role_fit": 0, "reason": "location-non-us-locked"}
    role_fit = 0
    neg = 0
    for pat, pts in TITLE_POSITIVE:
        if re.search(pat, t):
            role_fit += pts
    for pat, pts in TITLE_NEGATIVE:
        if re.search(pat, t):
            neg += pts
    skill = 0
    for pat, pts in SKILL_POSITIVE:
        if re.search(pat, d):
            skill += pts
    loc_pts = 0
    for pat in LOCATION_POSITIVE:
        if re.search(pat, text):
            loc_pts += 5
            break
    for pat in LOCATION_NEGATIVE:
        if re.search(pat, text):
            loc_pts -= 20
    total = role_fit + neg + skill + loc_pts
    watch_flags = []
    for pat, name in WATCH_PATTERNS:
        hay = loc if name == "non-us-metro" else text
        if re.search(pat, hay):
            watch_flags.append(name)
    # Hybrid/on-site anchored to a non-SF US metro (and no SF/remote-US presence
    # in the location fields) is not actionable for an SF-based applicant.
    NON_SF_US_METRO = r"\b(new york|nyc|austin|seattle|boston|denver|chicago|los angeles|atlanta|washington,?\s*d\.?c\.?|maryland|virginia|portland|phoenix|miami|dallas|houston)\b"
    sf_ok = re.search(r"\bsan francisco\b|\bbay area\b|\bremote\b", loc)
    anchored = re.search(r"\b(hybrid|on[- ]site|in[- ]office|in[- ]person)\b", text)
    if anchored and re.search(NON_SF_US_METRO, loc) and not sf_ok:
        watch_flags.append("onsite-outside-sf")
    # Compliance-channel notices are surfaced on their own tier: the notice is
    # itself the discovery signal, so they bypass the role-fit floor — but they
    # still had to pass every fit gate above. Resolve each to a live employer
    # application before staging; never apply to the notice text itself.
    if is_notice:
        return {"tier": "compliance-lead", "score": total, "role_fit": role_fit,
                "reason": "visa-notice-lead" + (";" + ";".join(watch_flags) if watch_flags else "")}
    # Qualification gates: role fit in the title is mandatory for actionable.
    if role_fit < ROLE_FIT_MIN:
        return {"tier": "watch" if (watch_flags or total >= ACTIONABLE_MIN) else "excluded",
                "score": total, "role_fit": role_fit,
                "reason": "no-role-fit-in-title" + (";" + ";".join(watch_flags) if watch_flags else "")}
    if total < ACTIONABLE_MIN:
        return {"tier": "watch", "score": total, "role_fit": role_fit,
                "reason": "below-actionable-floor" + (";" + ";".join(watch_flags) if watch_flags else "")}
    return {"tier": "actionable" if not watch_flags else "watch", "score": total,
            "role_fit": role_fit, "reason": ";".join(watch_flags) if watch_flags else "qualified"}

def main():
    con = sqlite3.connect(LEDGER)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT url, company, title, classification, description_sha256, evidence_path, date_posted, source "
        "FROM jobs WHERE live=1").fetchall()
    out = []
    for r in rows:
        desc = ""
        loc_ctx = ""
        ep = r["evidence_path"]
        if ep:
            p = Path(ep)
            if p.suffix == ".json":
                try:
                    raw = json.loads(p.read_text())
                    job = raw if isinstance(raw, dict) and "title" in raw else raw
                    desc = json.dumps(job)[:8000]
                    if isinstance(raw, dict):
                        loc_ctx = extract_location_context(raw)
                except Exception:
                    pass
        c = classify(r["title"], r["company"], desc, loc_ctx, r["classification"])
        if c["tier"] == "excluded" and c["reason"] == "no-role-fit-in-title" and c["score"] < ACTIONABLE_MIN:
            continue  # drop pure noise; keep watch/excluded-with-signal visible below threshold cut
        out.append({"tier": c["tier"], "score": c["score"], "role_fit": c["role_fit"],
                    "url": r["url"], "company": r["company"], "title": r["title"],
                    "source": r["source"], "date_posted": r["date_posted"],
                    "classification": r["classification"], "reason": c["reason"]})
    out.sort(key=lambda x: ({"actionable": 0, "compliance-lead": 1, "watch": 2,
                             "excluded": 3}[x["tier"]], -x["score"]))
    print(json.dumps(out[:80], indent=2))

if __name__ == "__main__":
    main()
