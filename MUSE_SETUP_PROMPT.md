# Prompt for a private Muse agent

Copy this prompt into a Muse agent after granting it access to your **private** `hiddenjob` repository:

```text
Use the private hiddenjob repository as a local, review-first job-discovery system.

First, read README.md and skills/hiddenjob/SKILL.md. Run the setup steps only in the user's private workspace. Create config/targets.json from config/targets.example.json and config/profile.json from config/profile.example.json. Never put either file, the .hiddenjob data directory, resumes, contact information, tokens, cookies, screenshots, application materials, or complaint records into Git.

Discover opportunities from publisher-declared robots.txt and sitemaps. Describe results neutrally: a posting may be less visible, poorly indexed, or absent from a measured search surface, but do not claim intentional concealment unless there is direct evidence. Preserve unmeasurable or blocked sources as unmeasurable; do not call them empty.

Use `python3 hiddenjob.py sync --limit 25`, review source evidence, then stage only jobs the user has approved. `apply-staged --limit N` may prefill only that bounded, approved set. Never send email, submit an ATS form, create accounts, solve CAPTCHAs, file an agency complaint, or make a public claim without an explicit final user instruction.

For possible discrimination concerns, use the local complaint ledger only to preserve evidence and track a draft. Keep EEOC and DOL OFCCP routing separate, check the current official agency pages and deadlines, and state that a case is not filed until the user completes the official process.
```
