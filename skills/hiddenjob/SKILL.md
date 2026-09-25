---
name: hiddenjob
description: Discover less-visible job postings from publisher-declared sitemaps, organize review-first applications, and maintain a private evidence and complaint-preparation ledger.
---

# hiddenjob

Use this skill when asked to find `$hiddenjobs`, jobs that may be poorly indexed or not surfaced by a site's search UI, or to centralize a job-search and application record.

## Purpose

Find postings that a person might otherwise miss because of sitemap structure, opaque URLs, weak indexing, or a separate careers system. Do **not** claim that an employer intentionally hid a posting. The evidence can support only what was observed: a publisher-declared URL, whether it appeared in a sitemap, its content at capture time, and whether it appeared in a separately measured search surface.

## Required workflow

1. Initialize a private local configuration: `python3 hiddenjob.py init`, then edit `config/targets.json` and copy `config/automation.example.json` to ignored `config/automation.json`. Keep profile and data files out of Git.
2. If the person supplies a URL list from `$hiddenjobs`, Muse, or another collector, place it in an ignored `config/hiddenjobs-urls.jsonl` file and add it with `url_list_file` in `config/targets.json`. An export may include descriptions, contacts, or application state; the importer supports JSONL records with a `url` key, JSON arrays, `{ "urls": [...] }`, or one URL per line, and retains only each URL. Direct URLs supplement—not replace—publisher `robots.txt` and sitemap discovery. Preserve the three outcomes: found, no declared relevant URL, or unmeasurable/blocked. Never convert a blocked result into a negative claim.
2b. Wire the ATS board registry: copy `config/hiddenjobs-targets.example.json` to ignored `config/hiddenjobs-targets.json` and set `"ats_targets_file": "hiddenjobs-targets.json"` in `config/targets.json`. `sync` then pulls each registry entry's public ATS board (Greenhouse, Ashby, Lever) through that board's own posting API — one HTTP call per board, no page scraping — and records every posting with the JSON response saved as evidence. Boards with `enabled: false`, missing `kind`/`board`, or an unsupported kind are skipped with a stderr note, never silently. Keep the registry's board slugs verified: probe each board's public API and only add entries that return 200 with real postings.
2c. Company hosts: entries under `company_hosts` in `config/targets.json` with `"enabled": true` are walked through that host's own `robots.txt`/sitemap with a bounded budget (`--max-host-sitemap-urls`, default 400), preferring career child maps and filtering URLs to job/career/position/opening paths. Hosts default to disabled; enable only hosts whose sitemaps are publisher-declared and measurable.
3. Run `python3 hiddenjob.py sync --limit 25`, inspect the captured records with `python3 hiddenjob.py jobs`, and open the saved source copy before staging an application.
4. Use the person's private resume and profile only in their private workspace to rank and stage jobs. Never put that data, evidence, or application materials in Git. With the `hands_off_with_final_approval` policy, automate routine discovery, evidence capture, ranking, staging, prefill, tracking, and reminders after the person chooses Muse task/site permissions.
5. Before a batch can submit, show the person its employer/role list, eligibility rules, and cap, then request one final approval. Only after it is approved set `HIDDENJOB_AUTOSUBMIT=1` and use `--submit --confirm-submit`. Account creation, passwords, one-time codes, CAPTCHAs, unclear questions, email, complaints, payments, and terms acceptance are always human-only. Muse cannot approve its own permission requests. Record `submitted` only after a real confirmation page. Keep every material claim tied to a captured source and time.

For repeatable processing, use `python3 hiddenjob.py apply-staged --limit N` only after the user has reviewed and staged each record. It runs the same prefill-by-default adapter and does not broaden submission authority.

## Visa-related wording

The classifier labels wording as `perm-like`, `lca-like`, or `recruitment-notice-like`; it does not decide an employer's immigration practice or legal compliance. An LCA notice can describe a position already being filled and is not automatically an open role. Review the actual posting and application instructions.

## EEOC and DOL OFCCP case preparation

Use the centralized complaint ledger only when a person describes a possible employment-discrimination issue and wants to preserve source evidence. It is never an automated reporting system.

- EEOC: protected-basis employment discrimination. Start from the official [charge process](https://www.eeoc.gov/how-file-charge-employment-discrimination).
- DOL OFCCP: possible disability or protected-veteran discrimination by a federal contractor or subcontractor. Start from the official [complaint process](https://www.dol.gov/agencies/ofccp/contact/file-complaint). Record contractor status as unknown unless supported by a source.
- Create a draft only: `python3 hiddenjob.py complaint create --agency eeoc|ofccp --employer 'Name' --alleged-date YYYY-MM-DD`.
- Attach a captured posting: `python3 hiddenjob.py complaint evidence --case N --url <captured-url>`.
- Explain that a draft is not filed. The person chooses whether to use the official agency route and must review deadlines.

Never invent protected-basis facts, contractor status, dates, or allegations. Do not submit an inquiry, complaint, email, or application without the person's explicit confirmation at the final step.
