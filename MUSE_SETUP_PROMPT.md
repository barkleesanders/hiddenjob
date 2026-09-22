# Prompt for a private Muse agent

Copy the prompt from the top of [README.md](README.md) into a Muse agent after granting it access to your **private** `hiddenjob` repository. It is duplicated here so the repository has one short handoff and one operational reference.

## Setup contract

The person using the system provides their own resume and profile to Muse privately. Muse writes only a local, ignored `config/profile.json` and must never commit it, uploaded resumes, evidence, screenshots, cookies, credentials, applications, or complaint records.

## Automation contract

Muse can automate discovery, source capture, resume-based ranking, evidence organization, staging, prefill, status tracking, and follow-up reminders. It starts in **review-first** mode.

A person can choose bounded automatic ATS submission only by explicitly saying `enable bounded auto-submit`, approving the eligibility rules and maximum number of applications per run, and setting the project-local environment gate. The run command is:

```bash
HIDDENJOB_AUTOSUBMIT=1 python3 hiddenjob.py apply-staged \
  --submit --confirm-submit --limit <approved-cap>
```

The agent must stop for login/account creation, passwords, CAPTCHAs, unclear employer questions, missing job evidence, and any result without a confirmation page. It must not send email, make public statements, or file a government complaint without a separate explicit instruction.

## Referral note

The README includes the Muse invitation code `FJBMD8`. Have the person redeem it in Muse **Settings** within 48 hours of joining so both people receive 1 billion Muse tokens.
