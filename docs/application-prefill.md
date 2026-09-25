# Auto-answering factual application questions

Some application questions are purely factual and can be answered from the
user's own local profile without asking every time. This keeps prefill
hands-off while holding the line on anything legal or judgment-based.

## What gets auto-answered

Answer directly from the gitignored local profile (`config/profile.json`,
never committed):

- **"How did you hear about this job?"** → the profile's `default_source`
  (e.g. `"Online job board"`). The user can override per application.
- **"Have you ever worked for {employer}?"** → check the profile's
  `employment_history` for a case-insensitive employer-name match.
  Match → Yes; no match → No. Never guess from memory — only from the
  profile data on disk.
- **Work authorization / sponsorship** → from the profile's
  `work_authorization` block, answered exactly as the user configured it.

## What never gets auto-answered

- Attestations, arbitration agreements, AI-usage policies, privacy-policy
  acknowledgments, non-compete disclosures, or any checkbox that accepts
  terms, waives rights, or makes a legal representation. These always stop
  for the user's explicit per-application approval.
- Free-text questions (e.g. "Why {company}?") — drafted from the user's
  materials for review, never submitted unseen.
- Anything not present in the profile. Missing data is a stop-and-ask,
  not an inference.

## Privacy boundaries

- The profile, employment history, and every real answer live in gitignored
  local state (`config/profile.json`, `.hiddenjob/`). This document uses
  placeholder values only.
- Auto-answer logic reads the local profile at prefill time; it never
  writes personal data into the repository, logs, or screenshots committed
  to Git.
- Example profile shape (fictional values):

```json
{
  "full_name": "Jordan Lee",
  "default_source": "Online job board",
  "work_authorization": { "authorized": true, "needs_sponsorship": false },
  "employment_history": [
    { "employer": "Example Corp", "title": "Support Engineer" }
  ]
}
```
