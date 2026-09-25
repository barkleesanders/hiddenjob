#!/usr/bin/env python3
"""Rank hiddenjob ledger postings against Barklee's profile.

Reads the SQLite ledger, scores each live posting on title/company/description
fit, hard-excludes Spanish-fluency-required roles, and prints a ranked shortlist
as JSON. Read-only: never mutates the ledger.
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
]
TITLE_NEGATIVE = [
    (r"\bintern\b", -50), (r"\bjunior\b", -15), (r"\bstaff\b.*\barchitect\b", -10),
    (r"\bprincipal\b.*\barchitect\b", -10), (r"\bdistinguished\b", -25),
    (r"\bvp\b", -25), (r"\bdirector\b", -20), (r"\bchief\b", -30),
]
HARD_EXCLUDE = [
    r"\bspanish\b.{0,60}\bfluent\b", r"\bfluent\b.{0,60}\bspanish\b",
    r"\bbilingual\b.{0,40}\bspanish\b", r"\bspanish\b.{0,40}\bbilingual\b",
]
LOCATION_POSITIVE = [r"\bremote\b", r"\bsan francisco\b", r"\bbay area\b", r"\bmenlo park\b",
                     r"\bunited states\b", r"\banywhere\b"]
LOCATION_NEGATIVE = [r"\b(london|berlin|toronto|dublin|sydney|singapore|tokyo)\b.{0,20}\bonly\b"]

def score(title, company, description):
    t = f"{title}".lower()
    d = f"{description or ''}".lower()[:4000]
    text = f"{t} {d}"
    for pat in HARD_EXCLUDE:
        if re.search(pat, text):
            return None, "spanish-fluency-required"
    s = 0
    for pat, pts in TITLE_POSITIVE:
        if re.search(pat, t):
            s += pts
    for pat, pts in TITLE_NEGATIVE:
        if re.search(pat, t):
            s += pts
    for pat in LOCATION_POSITIVE:
        if re.search(pat, text):
            s += 5
            break
    for pat in LOCATION_NEGATIVE:
        if re.search(pat, text):
            s -= 20
    # seniority sanity: exact C-suite / 15yr+ principal architect already handled
    return s, ""

def main():
    con = sqlite3.connect(LEDGER)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT url, company, title, classification, description_sha256, evidence_path, date_posted, source "
        "FROM jobs WHERE live=1").fetchall()
    # descriptions live in evidence files; load text cheaply for scoring
    ranked = []
    for r in rows:
        desc = ""
        ep = r["evidence_path"]
        if ep and Path(ep).suffix == ".json":
            try:
                raw = json.loads(Path(ep).read_text())
                job = raw if isinstance(raw, dict) and "title" in raw else raw
                desc = json.dumps(job)[:6000]
            except Exception:
                pass
        pts, reason = score(r["title"], r["company"], desc)
        if pts is None:
            continue
        ranked.append({"score": pts, "url": r["url"], "company": r["company"],
                       "title": r["title"], "source": r["source"],
                       "date_posted": r["date_posted"], "excluded": reason})
    ranked.sort(key=lambda x: -x["score"])
    print(json.dumps(ranked[:60], indent=2))

if __name__ == "__main__":
    main()
