# Per-job resume tailoring

The default flow attaches one base resume to every application. This workflow
tailors the resume to each staged job before the application is submitted.

## Pipeline

1. **Read the job description** for the staged role (posting URL is in the
   local application ledger).
2. **Tailor a copy of the base resume** against that JD:
   - Reframe and reorder existing experience to match the JD's keywords.
   - Never invent metrics, employers, dates, or achievements. If the JD asks
     for something with no evidence, omit it rather than fabricate it.
   - Preserve all dates, employers, and facts exactly.
   - ATS-compatible formatting: single column, standard section headers,
     left-aligned bullets, concise action verbs, two pages max.
     No emojis, no em dashes, no graphics or tables.
3. **Name the file** with the convention:

   `{Full Name} - {Job Title} +{Phone}.pdf`

   Example (fictional): `Jordan Lee - Senior Support Engineer +1-555-010-2030.pdf`

   Use the job title exactly as posted. On filesystems that forbid `/`,
   replace it with `-` in the local copy; keep the exact title in any
   cloud copy.
4. **Store locally** under a gitignored directory (e.g. `materials/resumes/`
   or outside the repo). Never commit tailored resumes to Git.
5. **Upload to the user's cloud folder** (e.g. Drive `Job Search/Resumes/`)
   so every version is organized and retrievable.
6. **Swap into the staged application**: replace the base-resume attachment
   with the tailored file during ATS prefill, before the final-approval
   submission step.

## Privacy boundaries

- The repository must never contain a real resume, a real name, a real phone
  number, or any record of which employers the user applied to. All of those
  live in gitignored local state (`.hiddenjob/`, `config/profile.json`,
  `materials/`) or the user's own cloud storage.
- This document uses placeholder values only. Any example that looks like a
  real person is fictional.
- Tailored resume content is derived from the user's own materials; it is
  reframing, not fabrication. Flag missing metrics instead of inventing them.
