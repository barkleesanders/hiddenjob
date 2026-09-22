# hiddenjob

`hiddenjob` is a private, configuration-first toolkit for discovering job postings that are easy to miss, preserving the source evidence, and organizing a review-first application and accountability ledger.

It starts from publisher-declared `robots.txt` and sitemap URLs rather than relying only on a site's search box. That can surface job pages with opaque URLs, weak indexing, or a separate careers system. It does **not** infer that a company intentionally concealed a job.

## What it does

- Walks declared sitemaps and captures job postings with source URL, capture time, hash, and local evidence copy.
- Labels certain wording as `perm-like`, `lca-like`, or `recruitment-notice-like` for human review. These are content labels, not legal determinations.
- Keeps a local application ledger: `staged`, `drafted`, `submitted`, `interview`, `offer`, `rejected`, `withdrawn`, or `closed`.
- Optionally prefills a staged ATS form through a user-installed local browser bridge. It uses a gitignored profile and stops for review by default.
- Keeps a separate local draft-case ledger for EEOC and DOL OFCCP routing, with captured evidence links and official filing instructions.
- Keeps personal configuration, evidence, resumes, application materials, and case records out of Git by default.

It deliberately does **not** send email, create accounts, solve CAPTCHAs, contact employers, or file complaints. The optional browser adapter only fills a reviewed ATS form by default. Its submit path requires `--submit`, `--confirm-submit`, `HIDDENJOB_AUTOSUBMIT=1`, and a real post-submit confirmation.

## Quick start

```bash
git clone git@github.com:YOUR-ACCOUNT/hiddenjob.git
cd hiddenjob
python3 hiddenjob.py init
# Edit config/targets.json before any network request.
python3 hiddenjob.py sync --limit 25
python3 hiddenjob.py jobs --classification perm-like
python3 hiddenjob.py stage 'https://example.com/jobs/123' --note 'Reviewed source and fit'
python3 hiddenjob.py apply 'https://example.com/jobs/123' --dry-run
python3 hiddenjob.py apply-staged --limit 3 --dry-run
python3 hiddenjob.py report
```

Run the standard-library test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Evidence states

| State | Meaning |
| --- | --- |
| Captured | The tool fetched the URL now, saved a local copy and hash, and recorded a time. |
| Unmeasurable | The host returned a block, challenge, error, or malformed sitemap. This is not evidence that it has no jobs. |
| Staged | A person reviewed the source and wants to consider applying. No application was sent. |
| Submitted | Record only after an actual confirmation from the employer's system. |
| Draft complaint case | A private evidence record, not a filed agency complaint. |

## Optional browser prefill

Copy `config/profile.example.json` to the ignored `config/profile.json`, add only the fields you want to offer to forms, and install a compatible local `fcdp` bridge. The adapter can validate its planned action without a browser:

```bash
python3 hiddenjob.py apply 'https://example.com/jobs/123' --dry-run
```

After reviewing the open form and evidence, a user who has separately enabled the environment gate can request submission. Account creation, passwords, and CAPTCHAs always stop for the user; a click without a confirmation page is recorded as unverified.

`apply-staged --limit N` provides the repeatable automation lane: it processes only the bounded set of jobs that the person already staged, preserving one result record per job. It inherits the same prefill-by-default and submission gates.

## EEOC and DOL OFCCP

The complaint ledger prevents application records and potential agency matters from being mixed together. It keeps two routes distinct:

- **EEOC** addresses protected-basis employment discrimination generally. The current official [charge process](https://www.eeoc.gov/how-file-charge-employment-discrimination) says filing deadlines are generally 180 days and may be 300 days in some jurisdictions.
- **DOL OFCCP** accepts complaints concerning disability or protected-veteran discrimination by covered federal contractors or subcontractors. Its current official [complaint process](https://www.dol.gov/agencies/ofccp/contact/file-complaint) states a 300-calendar-day deadline and explains that a pre-complaint inquiry does not extend it.

Create a local draft and attach already-captured evidence:

```bash
python3 hiddenjob.py complaint create \
  --agency ofccp --employer 'Example Employer' \
  --alleged-date 2026-09-01 --contractor-status unknown
python3 hiddenjob.py complaint evidence --case 1 --url 'https://example.com/jobs/123'
python3 hiddenjob.py complaint list
```

This is organizational support, not legal advice or a filing service. See [the routing guide](docs/complaint-routing.md), verify the official pages again before acting, and preserve the source evidence unchanged.

## Muse handoff

For a configured Muse agent, use the reviewed prompt in [MUSE_SETUP_PROMPT.md](MUSE_SETUP_PROMPT.md). It keeps the agent inside the private workspace and prohibits autonomous submissions, messages, or filings.

## Privacy boundary

Before a commit, run:

```bash
git grep -n -E -i '(@[^[:space:]]+\.(com|org|net)|phone|resume|linkedin|token|api[_-]?key|address)' || true
git status --short
```

Review every match. The examples use placeholders only; do not commit a real profile or `.hiddenjob/` data directory.

## License

[MIT](LICENSE)
