# Hidden-Channels Research — 2026-09-27

Deep-research report on (1) 2025–2026 Federal Register H-1B/PERM rulemaking,
(2) the immigration-compliance recruitment channels where employers post
low-visibility job notices, and (3) the jobs.now methodology — with ranked
recommendations for new hiddenjob discovery sources.

**Research method:** Barklee's VM-local deepsearch stack
(`~/workspace/skills/mini-deepsearch/SKILL.md`,
sha256 `dae694706af4705719e72142cd4dd7ac2c54570a4f1de6077a816d8aa969b59`;
canonical `~/workspace/skills/deepsearch/SKILL.md`,
sha256 `1db160b3550f2d5c677b9d87bfa04bf324e13a77035a33628a5ea717a6773f76`).
Six-phase method: scope → fan out (SearXNG, Linkup, Parallel, You.com, Tavily,
Brave, Jina, Exa, TinyFish, Marginalia) → read full sources → adversarially
verify → cite. All URLs below were fetched live on **2026-09-27** unless marked
"[search snippet]" (seen in provider results, page not fetched).

**Confidence tiers:** Strong = primary source read in full (regulation text,
Federal Register, agency page). Moderate = reputable secondary source read in
full (law firm, established press). Speculative = single-source, snippet-only,
or advocate claim.

---

## Executive summary

- **Barklee's core instinct is correct, but the premise needs a correction.**
  No 2025–2026 Federal Register rule has yet changed *how* employers must
  advertise jobs for H-1B/PERM purposes. What exists: (a) DHS's **weighted
  H-1B selection final rule** (Dec 29, 2025) — changes the lottery to
  wage-weighted selection, not advertising; (b) DOL's **prevailing-wage NPRM**
  (Mar 27, 2026) — changes wage math, not advertising; (c) a **PERM
  modernization NPRM** ("Modernizing the Labor Market Test…", RIN 1205-AC29)
  that *would* rewrite recruitment standards — but as of 2026-09-27 it is
  still only on the Unified Agenda and **has not been published** in the
  Federal Register. **Strong.**
- The actual "hidden" channels are the **unchanged-since-2004 PERM
  recruitment rules** at 20 CFR 656.17: two **Sunday newspaper ads**, a
  30-day **State Workforce Agency job order**, plus three of ten optional
  steps (job fairs, employer site, job-search site, campus, trade orgs,
  private firms, referral programs, **local/ethnic newspapers**,
  **radio/TV**). Employers running minimal-compliance labor-market tests
  concentrate postings in Sunday classifieds that few job seekers read.
  **Strong** (regulation text read in full).
- **jobs.now** (jobs.now) is a CIS-backed job board that scrapes exactly
  these PERM-mandated channels — "a proprietary sourcing process that
  identifies jobs exclusively from locations legally required by the PERM
  process." 4,500+ postings, 70,000+ applications, 1,500+ companies; full
  XML sitemaps make it directly crawlable. **Strong.**
- The highest-value new hiddenjob source is the **jobs.now sitemap feed**
  itself, followed by **DOL OFLC disclosure data** (employer targeting) and
  the **National Labor Exchange / US.jobs** (the SWA job-order channel).
  Details in §5.

---

## 1. Topic 1 — 2025–2026 Federal Register H-1B/PERM actions

### 1a. DHS Weighted Selection Process for H-1B — FINAL RULE (Dec 29, 2025) ✅

- **Title:** "Weighted Selection Process for Registrants and Petitioners
  Seeking To File Cap-Subject H-1B Petitions"
- **Agency:** Department of Homeland Security / USCIS
- **Citation:** 90 FR (Dec 29, 2025), FR Doc 2025-23853 —
  https://www.federalregister.gov/documents/2025/12/29/2025-23853/weighted-selection-process-for-registrants-and-petitioners-seeking-to-file-cap-subject-h-1b
  (verified live via FR API, 2026-09-27). **Strong.**
- **What it changes:** Replaces the random H-1B registration lottery with a
  **wage-weighted selection process** favoring higher-paid (higher wage-level)
  beneficiaries. USCIS announcement: "DHS Changes Process for Awarding H-1B
  Work Visas to Better Protect American Workers" —
  https://www.uscis.gov/newsroom/news-releases/dhs-changes-process-for-awarding-h-1b-work-visas-to-better-protect-american-workers
  [search snippet]. **Moderate.**
- **Effect on job advertising channels:** None. This rule changes *selection
  among registrations*, not recruitment or posting obligations. It does not
  name newspapers, radio, job boards, or any advertising channel.
  **Strong** (from the rule's abstract and USCIS materials).

### 1b. DOL "Improving Wage Protections…" — PROPOSED RULE (Mar 27, 2026) ✅

- **Title:** "Improving Wage Protections for the Temporary and Permanent
  Employment of Certain Foreign Nationals in the United States"
- **Agency:** DOL Employment and Training Administration
- **Citation:** 91 FR 15454–15501 (Mar 27, 2026), FR Doc 2026-06017,
  Docket ETA-2026-0001, RIN 1205-AC30 —
  https://www.govinfo.gov/content/pkg/FR-2026-03-27/html/2026-06017.htm
  (full text read, 2026-09-27). DOL press release:
  https://www.dol.gov/newsroom/releases/eta/eta20260326-0 (read, 2026-09-27).
  **Strong.**
- **What it changes:** Revises the four-tier **prevailing-wage methodology**
  (20 CFR 655/656) using BLS OEWS percentile thresholds, raising wage floors
  for H-1B, H-1B1, E-3, and PERM. Comment period closed May 26, 2026.
- **Effect on job advertising channels:** None directly. It governs the wage
  that must be *offered* (and therefore the wage floor stated in ads), not
  *where* employers must advertise. The rule's 10,000+ lines contain no
  revision to 656.17 recruitment steps. **Strong** (verified against the
  full NPRM text: the action amends wage computation only).

### 1c. DOL PERM "Modernizing the Labor Market Test…" — NOT YET PUBLISHED ⚠️

- **Title (agenda):** "Modernizing the Labor Market Test and Improving
  Protections for U.S. Workers in the PERM Immigrant Visa Program (NPRM)"
- **Agency:** DOL/ETA, RIN 1205-AC29, 20 CFR 656 —
  https://www.reginfo.gov/public/do/eAgendaViewRule?RIN=1205-AC29&operation=OPERATION_PRINT_RULE&pubId=202510
  (read, 2026-09-27). **Strong.**
- **Status:** Unified Agenda lists it at "Proposed Rule Stage" with an NPRM
  timetabled 07/2026 and **"RIN Data Printed in the FR: No."** A direct
  FederalRegister.gov API query for PERM proposed rules published in 2026
  returns exactly **one** result — the wage NPRM (2026-06017) above. **The
  recruitment-reform NPRM has not been published as of 2026-09-27.**
  **Strong.**
- **Why it matters anyway:** The agenda abstract says PERM rules "have not
  been comprehensively modified since 2004," cites "advancements in
  technology and changes that have altered industry practices in key areas,
  **including recruitment**," and promises "improving the minimum standards
  for recruiting qualified U.S. workers." This is the rulemaking Barklee is
  sensing — the administration *wants* to rewrite the recruitment-channel
  rules, which confirms those channels are where minimal-compliance behavior
  concentrates — but the text does not exist yet. Analysis:
  https://www.murthy.com/2026/07/15/dol-signals-major-modernization-of-perm-program-through-new-proposed-rulemaking
  (read, 2026-09-27). **Moderate.**
- **Watch item for hiddenjob:** when this NPRM publishes, its preamble will
  explicitly enumerate the recruitment channels DOL believes are
  underperforming (likely Sunday print ads, obscure journals, odd-hour
  radio). That preamble becomes the authoritative "where they hide jobs"
  map. Recommend a watch for RIN 1205-AC29 hitting the Federal Register.

### 1d. Context: earlier H-1B rules (for the record)

- **H-1B Modernization final rule** (Dec 18, 2024, FR 2024-29354,
  Biden-era DHS): "Modernizing H-1B Requirements, Providing Flexibility in
  the F-1 Program…" —
  https://www.federalregister.gov/documents/2024/12/18/2024-29354/modernizing-h-1b-requirements-providing-flexibility-in-the-f-1-program-and-program-improvements
  [search snippet]. **Moderate.**
- **H-1B registration integrity final rule** (Feb 2, 2024, FR 2024-01770):
  beneficiary-centric selection —
  https://www.federalregister.gov/documents/2024/02/02/2024-01770/improving-the-h-1b-registration-selection-process-and-program-integrity
  [search snippet]. **Moderate.**
- Neither changed recruitment advertising channels.

### Topic 1 bottom line

Barklee's "reverse-engineer the improvements" strategy is sound in spirit —
the pending PERM NPRM's target list *will* be the map — but there is **no
published 2025–2026 rule changing advertising channels to reverse-engineer
yet**. The channels that matter today are the 2004-era PERM rules in §2,
which the administration itself says are outdated. **Strong.**

---

## 2. Topic 2 — Where employers post compliance-driven recruitment

### 2a. PERM mandatory recruitment (20 CFR 656.17) — the channel list

Source: https://www.law.cornell.edu/cfr/text/20/656.17 (full text read,
2026-09-27). **Strong.**

**Professional occupations** — all steps within 6 months before filing
(mandatory steps: 30–180 days before filing):

| # | Step | Channel | Visibility to job seekers |
|---|------|---------|---------------------------|
| M1 | SWA job order, 30 days | State Workforce Agency job bank | Low — state job banks, not aggregators |
| M2 | Two Sunday ads | **Newspaper of general circulation** (or 1 Sunday ad + 1 professional-journal ad for advanced-degree roles) | **Very low** — Sunday classifieds |
| A1–A3 | Three of ten: | | |
| | (A) Job fairs | In-person | Low |
| | (B) Employer's website | Company careers page | Medium |
| | (C) Job-search website (non-employer) | e.g. LinkedIn/Indeed | High |
| | (D) On-campus recruiting | Universities | Low |
| | (E) Trade/professional orgs | Newsletters, trade journals | Low |
| | (F) Private employment firms | Recruiters | Low |
| | (G) Employee referral program | Internal | None (external) |
| | (H) Campus placement offices | Universities | Low |
| | (I) **Local and ethnic newspapers** | Community papers | **Very low** |
| | (J) **Radio and television** | Broadcast, any hour | **Very low / ephemeral** |

**Nonprofessional occupations:** only M1 (SWA job order) + M2 (two Sunday
newspaper ads). **Strong.**

Ad-content rules (§656.17(f)): ads must name the employer, direct applicants
to send resumes **to the employer**, describe the vacancy, state the work
location, and offer ≥ prevailing wage. So these are *genuine, apply-able
openings* — a qualified U.S. applicant must by law be considered.
**Strong.**

### 2b. H-1B LCA posting (20 CFR 655.734) — the channel list

Sources: DOL WHD Fact Sheet #62M —
https://www.dol.gov/agencies/whd/fact-sheets/62m-h1b-notice (read,
2026-09-27); notice-content summary —
https://www.gzimmigration.com/expertise/non-immigrant-visa-niv/h-1b-professional/notice-of-posting-requirements/
(read, 2026-09-27). **Strong.**

- **No labor-market test for H-1B.** The employer files an LCA attesting to
  wage/working conditions; there is no requirement to recruit U.S. workers
  first. (CIS states this explicitly —
  https://cis.org/JobsNow/Jobs-Now-Americans; **Moderate**, advocate source
  but consistent with the statute.)
- **Notice requirement:** on/within 30 days before filing the LCA, the
  employer must notify U.S. workers via (a) notice to the bargaining rep, or
  (b) **hardcopy posting at two conspicuous worksite locations for 10
  days**, or (c) **electronic notice to all workers at the worksite for 10
  days** (email, electronic bulletin board). **Strong.**
- The notice states the number of H-1B workers sought, occupation, wage
  offered, period, and locations — i.e., it *describes a real opening* — but
  it is an **internal** notice, not a public job ad. Scrapability: ~zero
  unless the employer uses a public intranet. **Strong.**
- **Implication:** H-1B *LCA* notices are not a useful discovery channel;
  PERM *recruitment ads* are.

### 2c. Reporting on minimal-compliance / obscure-channel behavior

- **DOJ enforcement pattern.** Apple settled for **$25M** (Nov 2023) and
  Meta/Facebook settled (2021) over DOJ claims of INA discrimination during
  PERM labor-market tests. The alleged practices, per CIS's review of the
  case briefs: **not listing PERM roles on company websites** (unlike normal
  openings), **requiring postal-mail-only applications**, and not using
  ordinary recruiting processes — so "very few or no Americans noticed or
  successfully applied." CIS: https://cis.org/JobsNow/Jobs-Now-Americans
  (read, 2026-09-27). Apple settlement figure: Forbes/Reuters/CNBC, Nov 2023
  [search snippets; Reuters page 500'd on fetch — logged as negative
  result]. **Moderate** for the practice pattern (advocate + press
  characterization of court filings).
- **Community monitoring.** A widely shared TeamBlind post directs workers
  to jobs.now to find "jobs that are being posted in literal *newspapers*
  that no one sees… so they can claim that they needed to open up H1B and
  Perm processes," notes some postings "ask you to physically mail
  applications" (e.g., Instacart), and advises following the posting's own
  instructions then reporting to DOL —
  https://www.teamblind.com/post/tech-companies-committing-h1b-perm-fraud-apply-to-these-hidden-jobs-and-report-them-to-dept-of-labor-g3oghv3p
  (read, 2026-09-27). A Reddit r/cscareerquestions thread titled
  "Jobs.now exposes PERM jobs that are hidden on purpose from [Americans]"
  exists (https://www.reddit.com/r/cscareerquestions/comments/1n1a44s/jobsnow_exposes_perm_jobs_that_are_hidden_on/
  [search snippet; reddit.com blocked by fetch policy — negative result]).
  **Moderate** (community sources, consistent with the DOJ pattern above).
- **The Sunday-paper mechanism, concretely:** because §656.17 *requires*
  print Sunday ads but *permits* the other three steps to be low-visibility
  (job fair, trade journal, ethnic paper, radio), a minimal-compliance
  employer can satisfy the letter of the law while reaching ~zero active job
  seekers. The ads themselves are genuine openings with employer name,
  resume instructions, and wage ≥ prevailing wage. **Strong** (regulation +
  enforcement record).

### 2d. Candidate machine-readable sources (channel inventory)

| Source | URL | What's in it | Update cadence | Machine-readable? | Access limits |
|--------|-----|--------------|----------------|-------------------|---------------|
| **jobs.now sitemaps** | https://www.jobs.now/sitemap.xml → `sitemap-jobs-1.xml`, `sitemap-companies-*.xml`, `sitemap-locations.xml` | Individual PERM-notice job pages: title, employer, location, salary, REF code, application instructions ("Apply By Mail" flags) | Listings show "5d ago"–"2w ago" — refreshed within days/weeks | **Yes — plain XML sitemaps, no auth** | None observed; polite crawl rate advised |
| **DOL OFLC performance/disclosure data** | https://www.dol.gov/agencies/eta/foreign-labor/performance | Quarterly + FY disclosure files for PERM, H-1B LCA, prevailing wage: employer, occupation, wage, worksite, case status | Quarterly | **Yes — downloadable files** (also mirrored at http://catalog.data.gov/dataset/office-of-foreign-labor-certification-oflc-case-disclosure-data) | None; public |
| **h1bdata.info** | https://h1bdata.info/ | Searchable index of DOL LCA disclosure data: 3.8M+ records Apr 2016–Jun 2026, by employer/title/location/salary | Through Jun 2026 (as displayed) | Partial — searchable web UI; no documented API | None observed for browsing |
| **National Labor Exchange / US.jobs** | https://usnlx.com/ (about: https://usnlx.com/about/) → job seeker front end https://us.jobs | The SWA job-order channel itself: 300,000 employers, ~3M jobs/day from corporate career sites + state job banks + federal sites; all 50 states participate | Daily refresh, "no dead links" | Web search UI; bulk/API access is via partnership (DirectEmployers) | Job-seeker search is open; bulk feed is partner-gated |
| **Newspaper PERM classifieds** | Fragmented per-paper (e.g., papers selling PERM ad placement; `miaminewtimes.com/perm-advertising/` exists but was fetch-blocked — negative result) | Raw Sunday-ad text: employer, job title, resume instructions, REF codes | Weekly (Sunday) | **No** — HTML classifieds, per-paper formats | Paywalls on some papers |
| **PERM ad agencies** | https://perm-ads.com/ [search snippet] | Agencies that *place* PERM ads (immigration advertising) — useful for learning which papers carry them, not a job list | N/A | No | N/A |
| **FederalRegister.gov API** | https://www.federalregister.gov/api/v1/documents.json | Watch RIN 1205-AC29 for the PERM recruitment NPRM | Daily | **Yes — JSON API, no key** | None |

Radio/TV ads (§656.17(e)(1)(ii)(J)) are deliberately excluded as a discovery
source: ephemeral broadcasts with no public archive are effectively
unscrapable. **Strong** (assessment).

---

## 3. Topic 3 — jobs.now methodology

Source base: https://www.jobs.now/ (homepage + job page + sitemaps read,
2026-09-27); https://cis.org/JobsNow/Jobs-Now-Americans (read, 2026-09-27).
**Strong** for site-observed facts; **Moderate** for internal process claims
(self-described).

- **What it is:** "Discover the Hidden Job Market… Your gateway to exclusive
  jobs for US Citizens" (homepage). A job board for **H-1B PERM job
  postings** — roles employers must advertise in "specific outlets, like
  Sunday newspapers" to prove no qualified U.S. workers are available.
  **Strong.**
- **Who runs it:** the team behind the Center for Immigration Studies'
  "Jobs Now for Americans" project — "the team behind Jobs.Now decided to
  take action" after reviewing newspaper classifieds and finding OpenAI,
  Instacart, etc. ads requesting postal-mail applications for roles absent
  from company websites. Claims "as featured in Newsweek" (homepage).
  **Moderate** (self-described; Newsweek feature not independently verified —
  logged).
- **Sourcing methodology (their words):** "a **proprietary sourcing process
  that identifies jobs exclusively from locations legally required by the
  PERM process** for sponsoring immigrant workers for green cards" — i.e.,
  they monitor the PERM-mandated channels (Sunday newspaper classifieds in
  major metros) and transcribe the ads. Coverage cities: San Francisco, New
  York, Boston, Atlanta, Chicago, Houston, Seattle, Charlotte, Salt Lake
  City (CIS page); homepage currently shows Phoenix-area listings.
  **Moderate** (proprietary = unverifiable internals, but the output —
  REF-coded newspaper-style listings — is consistent with the claim).
- **Scale claimed:** "over 4,500 job postings, generating over 70,000
  applications at over 1,500 companies" (CIS page). **Moderate**
  (self-reported; the sitemap-jobs-1.xml observed live contains hundreds of
  URLs, consistent with thousands-scale).
- **Update cadence (observed):** homepage listings tagged "5d ago", "1w
  ago"; a sampled job page's related listings tagged "2w ago" — i.e.,
  **ingest within the last ~2 weeks**, faster than the 30–180-day PERM
  recruitment window. **Strong** (directly observed 2026-09-27).
- **What makes it different from LinkedIn/Indeed:** (1) source channels —
  Sunday print classifieds, not employer ATS feeds or crawled career pages;
  (2) the listings are ones employers have an incentive to keep obscure
  (absent from company sites/LinkedIn per the DOJ pattern); (3) each listing
  preserves the ad's **application instructions** (postal-mail addresses,
  REF codes, "Apply By Mail" flags) — the compliance-relevant metadata
  aggregators discard. **Strong** (observed + DOJ-pattern corroboration).
- **Machine readability (observed):** full XML sitemap index at
  https://www.jobs.now/sitemap.xml with `sitemap-jobs-1.xml` (individual
  `/jobs/<id>-<slug>` URLs containing REF codes), `sitemap-companies-*.xml`,
  `sitemap-locations.xml`, category sitemaps. No auth, no key. A job detail
  page renders related jobs server-side; the primary job's full detail block
  appears JS-dependent (only "Related Jobs" rendered in text fetch) —
  **recommend fetching job pages with a JS-capable reader or checking for a
  JSON API backing the page**. **Strong** (directly observed).
- **How hiddenjob already uses it:** the local ledger already has a
  `jobs.now` source entry (per the Sept 26 sync: 325 postings across 13
  sources *including* jobs.now), and Barklee's 2026-09-27 ~12:55 PDT
  correction established `compliance-lead` as a first-class ranker tier for
  exactly these perm-style/lca-like/recruitment-notice listings rather than
  excluding them. This research validates that correction. **Strong**
  (local state + standing memory).

---

## 4. Adversarial verification notes

1. **Premise check — "the administration posted new H-1B job-posting rules
   on the Federal Register":** PARTLY FALSE. Two real 2025–2026 FR actions
   exist (weighted selection final rule; prevailing-wage NPRM) but neither
   touches advertising channels. The recruitment-channel rewrite (RIN
   1205-AC29) is agenda-only. The FR API query is the decisive negative
   evidence. **Strong.**
2. **"H-1B requires no labor market test":** True for the LCA process (20
   CFR 655) — attestation-based, no recruitment. The labor-market test
   attaches to PERM (20 CFR 656). CIS's phrasing is accurate on this point.
   **Strong.**
3. **"These newspaper jobs are real openings you can apply to":** True by
   regulation — §656.17(f) requires the ad to name the employer, give resume
   instructions, and offer ≥ prevailing wage; a qualified U.S. applicant must
   be considered. Whether any *specific* employer behaves fairly is
   case-by-case (see Apple/Meta settlements). **Strong** for the regulatory
   claim; **Moderate** for employer-behavior generalizations.
4. **jobs.now's 4,500/70,000/1,500 figures:** self-reported, not
   independently audited. The sitemap scale is consistent but not a full
   count. **Moderate.**
5. **"Radio stations" as a hiding channel:** legally real
   (§656.17(e)(1)(ii)(J)) but practically unscrapable — correctly deprioritized.
   **Strong** (assessment).

---

## 5. Recommended new hiddenjob discovery sources (ranked by expected value)

1. **jobs.now sitemap crawl** — Add a `jobsnow_sitemap` source:
   `sitemap.xml` → `sitemap-jobs-1.xml` → `/jobs/<id>-<slug>` pages.
   Pre-filtered PERM-notice leads with REF codes, salaries, locations, and
   apply-by-mail flags; refreshed within days. Maps directly onto the new
   `compliance-lead` tier. Investigate the page's backing JSON API for full
   detail extraction (text fetch only rendered related jobs).
2. **DOL OFLC disclosure data** (quarterly) — Build an employer-watchlist
   feed: employers with large certified-PERM volumes are the highest-
   probability sources of fresh Sunday-ad notices. Cross-reference with
   jobs.now and newspaper classifieds.
3. **RIN 1205-AC29 Federal Register watch** — A lightweight poll of
   `federalregister.gov/api/v1/documents.json` for the PERM "Modernizing
   the Labor Market Test" NPRM. Its preamble will be the authoritative map
   of which channels DOL considers underperforming — feed its channel list
   back into source priorities.
4. **National Labor Exchange / US.jobs** — The SWA job-order channel that
   PERM *mandates*. Overlaps aggregators, but it is the legally required
   posting location; worth a targeted source for roles missing elsewhere.
   Bulk access is partner-gated; start with job-seeker search queries.
5. **Newspaper classifieds (Sunday editions, major PERM metros)** — Direct
   source of raw ad text. Fragmented and mostly non-machine-readable;
   prioritize papers known to sell PERM placement (ad agencies like
   perm-ads.com reveal which papers). Consider OCR pipelines only if 1–4
   prove insufficient.
6. **h1bdata.info** — LCA-side employer targeting (3.8M records). Lower
   priority: LCAs don't require public recruitment, so this finds
   *employers*, not hidden postings.

**Explicitly not recommended:** radio/TV ad monitoring (ephemeral,
unarchived); treating H-1B LCA *notices* as a discovery channel (internal
postings, not public).

---

## 6. Negative results log

- `deepsearch.sh` query "2026 Federal Register H-1B recruitment advertising
  job posting rule DOL proposed final" returned 0 results (other phrasings
  succeeded).
- reddit.com/r/cscareerquestions PERM thread: fetch blocked by policy;
  title captured from search snippet only.
- miaminewtimes.com/perm-advertising/: fetch blocked by policy.
- Reuters Apple-settlement article (2023-11-09): HTTP 500 on fetch, 3
  attempts exhausted.
- jobs.now/about: HTTP 404 (no about page; methodology taken from homepage
  + CIS page instead).
- Newsweek feature claim for jobs.now: not independently verified.
- FR API confirms no published 2026 PERM recruitment NPRM (only the wage
  NPRM matches).

---

*Report written 2026-09-27 by the deepsearch research subagent. All fetches
performed live on 2026-09-27 (America/Los_Angeles).*
