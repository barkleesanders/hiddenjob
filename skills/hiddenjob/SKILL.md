---
name: hiddenjob
description: Discover less-visible job postings from publisher-declared sitemaps, organize review-first applications, and maintain a private evidence and complaint-preparation ledger.
---

# hiddenjob

Use this skill when asked to find `$hiddenjobs`, jobs that may be poorly indexed or not surfaced by a site's search UI, or to centralize a job-search and application record.

## Purpose

Find postings that a person might otherwise miss because of sitemap structure, opaque URLs, weak indexing, or a separate careers system. Do **not** claim that an employer intentionally hid a posting. The evidence can support only what was observed: a publisher-declared URL, whether it appeared in a sitemap, its content at capture time, and whether it appeared in a separately measured search surface.

## Required workflow

1. Initialize a private local configuration: `python3 hiddenjob.py init`, then edit `config/targets.json`. Keep profile and data files out of Git.
2. Discover from the publisher's `robots.txt` and sitemap first. Preserve the three outcomes: found, no declared relevant URL, or unmeasurable/blocked. Never convert a blocked result into a negative claim.
3. Run `python3 hiddenjob.py sync --limit 25`, inspect the captured records with `python3 hiddenjob.py jobs`, and open the saved source copy before staging an application.
4. Stage only reviewed records: `python3 hiddenjob.py stage <url> --note 'why this is a fit'`. The optional `apply` adapter uses a private local profile to prefill an ATS form and stops for review by default.
5. Do not request browser submission unless the user explicitly asks at the final step. It needs `--submit`, `--confirm-submit`, and `HIDDENJOB_AUTOSUBMIT=1`; account creation, passwords, and CAPTCHAs are always human-only. Record `submitted` only after a real confirmation page. Keep every material claim tied to a captured source and time.

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
