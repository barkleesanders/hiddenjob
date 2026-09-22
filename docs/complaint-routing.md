# Employment-complaint routing and case ledger

This package can preserve posting evidence and track a **draft** case. It cannot decide whether discrimination occurred, whether an employer is covered, or whether someone should file. It never submits a complaint.

Use the official agency process only after reviewing the facts, the applicable deadline, and the agency's current instructions.

| Route | Use it to evaluate | Important timing | Official route |
| --- | --- | --- | --- |
| EEOC | Employment discrimination based on a protected basis. A company being a federal contractor does not, by itself, establish an EEOC claim. | Usually 180 days; it may be 300 days when an applicable state or local agency enforces a parallel law. | [How to file a charge](https://www.eeoc.gov/how-file-charge-employment-discrimination) |
| DOL OFCCP | Employment or applicant discrimination by a federal contractor/subcontractor based on disability or protected-veteran status. The program stores contractor status as `unknown`, `reported`, or `verified`; it does not guess. | OFCCP says complaints must be filed within 300 calendar days of the alleged action. A pre-complaint inquiry does not extend that deadline. | [OFCCP complaint process](https://www.dol.gov/agencies/ofccp/contact/file-complaint) |

## What to centralize

For each possible case, keep the original job URL, capture time, saved source copy and hash, employer name and location, application status, the exact action being questioned, dates, and only the documents the person is comfortable providing. Record whether a case is `draft`, `submitted`, or `closed` only after the corresponding real-world event.

`hiddenjob complaint create` produces a local draft record and prints the appropriate official route. `hiddenjob complaint evidence` attaches an already-captured posting to that case. Neither command transmits information to EEOC, DOL, an employer, or any third party.

## Filing safeguards

- Use a pre-complaint inquiry when the OFCCP route is uncertain; OFCCP says it will not notify the employer about the inquiry. A formal OFCCP complaint does notify the employer.
- Do not wait for a tool review when a deadline is near. The official EEOC and OFCCP pages have the current filing instructions.
- Treat federal-contractor status as a fact requiring a source, not an inference from a company name or a job advertisement.
- Preserve the posting and application record exactly as obtained. Add observations separately; do not alter source evidence.

These instructions summarize official pages checked on 2026-09-22. They are operational guidance, not legal advice.

