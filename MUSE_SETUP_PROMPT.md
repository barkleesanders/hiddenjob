# Prompt for a private Muse agent

Copy the prompt from the top of [README.md](README.md) into a Muse agent after granting it access to your **private** `hiddenjob` repository. It is duplicated here so the repository has one short handoff and one operational reference.

## Setup contract

The person using the system provides their own resume and profile to Muse privately. Muse writes only local, ignored `config/profile.json` and `config/automation.json` files and must never commit them, uploaded resumes, evidence, screenshots, cookies, credentials, applications, or complaint records.

## Automation contract

Muse can automate discovery, source capture, resume-based ranking, evidence organization, staging, prefill, status tracking, and follow-up reminders. The default `hands_off_with_final_approval` policy is in `config/automation.example.json`.

At setup, Muse should ask the person once to choose their routine task/site approvals in Muse. It should then perform all approved routine work without repeated interruptions. Before a submission batch, Muse must show the person the exact employers, roles, eligibility rules, and count and request one final approval. After that approval, it sets the project-local environment gate and runs:

```bash
HIDDENJOB_AUTOSUBMIT=1 python3 hiddenjob.py apply-staged \
  --submit --confirm-submit --limit <approved-cap>
```

The agent must stop for login/account creation, passwords, one-time codes, CAPTCHAs, unclear employer questions, missing job evidence, and any result without a confirmation page. It must not send email, make public statements, accept terms, make payments, or file a government complaint without a separate explicit instruction. Muse cannot and must not try to approve its own permissions; the person controls Muse's persistent task/site approvals and the final submission approval.

## Referral note

The README includes the Muse invitation code `FJBMD8`. Have the person redeem it in Muse **Settings** within 48 hours of joining so both people receive 1 billion Muse tokens.
