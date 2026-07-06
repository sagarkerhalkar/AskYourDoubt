# AskYourDoubt 1.5.0 Requirement Traceability

This document maps each explicit product requirement to implementation and evidence. “Test each word” is treated as requirement-by-requirement verification: automated testing cannot prove that every source-code token executed, so source compilation/parsing, route import, browser tests, responsive rendering, coverage, and behavior tests are combined.

Status meanings:

- **PASS** — executed locally or validated by an executed automated source contract.
- **NOT RUN** — configured or designed but not executed in the local environment.
- **FAIL** — executed and failed. No requirement below is currently marked FAIL.

## Global design and experience

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| UI-01 | All oversized headings reduced globally | Final 1.5.0 CSS heading hierarchy; computed browser heading test | PASS |
| UI-02 | Top teacher/student boxes approximately 50% smaller | Teacher dashboard 168 px, teacher live 164 px, student welcome 150 px minimums; responsive screenshots | PASS |
| UI-03 | Professional international institute/SaaS appearance | Navy/blue/teal/neutral tokens, compact layouts, screenshots | PASS |
| UI-04 | Sellable commercial visual quality | Commercial landing/role portals, consistent card/forms/tables, no public development credit | PASS |
| UI-05 | Restrained animation and 3D depth | Fine-pointer hover depth, live indicators, reveal motion, glass/depth surfaces | PASS |
| UI-06 | Animation must not look like a game | Controlled transforms, limited gradients, small motion distances | PASS |
| UI-07 | Touch/mobile must not depend on hover | `@media(hover:none)` contracts and mobile browser checks | PASS |
| UI-08 | Reduced-motion accessibility | `prefers-reduced-motion:reduce` contract | PASS |
| UI-09 | No visible auto-refresh flicker | Signature-based DOM updates and no-store one-second fetch | PASS |
| UI-10 | No external font loading delay | Google Font requests removed | PASS |
| UI-11 | Replaceable high-resolution logo | SVG default plus admin brand upload | PASS |
| UI-12 | Public author/AI credit hidden | Template and live-browser assertions | PASS |

## Student requirements

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| ST-01 | Join using QR or direct teacher link | Join route, QR generation, live tests | PASS |
| ST-02 | Full name required | Join validation tests | PASS |
| ST-03 | Mobile exactly 10 numeric digits | Join validation tests | PASS |
| ST-04 | Student pages do not expose teacher/admin navigation | Role privacy tests | PASS |
| ST-05 | Closed session shows dedicated state | Closed-session flow test | PASS |
| ST-06 | Question text compulsory | Submission validation tests | PASS |
| ST-07 | Emoji-capable writing experience | Emoji upload/composer tests and UI contract | PASS |
| ST-08 | Optional attachment | Submission tests with and without file | PASS |
| ST-09 | Actual file maximum 10 MB | Exact 10 MB PASS and >10 MB rejection tests | PASS |
| ST-10 | PDF allowed | Upload matrix | PASS |
| ST-11 | Word allowed | Upload matrix | PASS |
| ST-12 | TXT allowed | Upload matrix | PASS |
| ST-13 | Image allowed | Upload matrix | PASS |
| ST-14 | Video-file doubts rejected | Upload matrix | PASS |
| ST-15 | Own question marked `My Question` | Live ranking/marker test | PASS |
| ST-16 | Student cannot vote own question | Vote tests | PASS |
| ST-17 | Another student votes once | Unique vote tests | PASS |
| ST-18 | Vote count controls ranking | Ranking tests | PASS |
| ST-19 | Live queue updates silently every second | Template contract and live polling browser test | PASS |
| ST-20 | Typed text preserved during polling | Live Chromium test | PASS |
| ST-21 | Highest-voted doubts appear first | API and rendered ranking tests | PASS |
| ST-22 | Skipped doubts hidden | Lifecycle tests | PASS |
| ST-23 | Completed doubts move to Answered | Lifecycle/tab tests | PASS |
| ST-24 | Other attachments hidden by default | Permission tests | PASS |
| ST-25 | Download appears only when permitted and file exists | Permission/render tests | PASS |
| ST-26 | Teacher resources directly available | Resource tests | PASS |
| ST-27 | Session name uses medium/compact scale | Computed typography and screenshots | PASS |
| ST-28 | Countdown displayed | Template/browser rendering | PASS |
| ST-29 | Submit redirects to Live | Submission flow tests | PASS |
| ST-30 | Selected tab survives refresh | Tab route/query tests | PASS |
| ST-31 | Live panel can minimize | Chromium focus-control test | PASS |
| ST-32 | Live panel can maximize | Chromium focus-control test | PASS |
| ST-33 | Live panel can use browser full screen | Source/browser control contract | PASS |
| ST-34 | Live panel can open new window | Protected focus route and browser test | PASS |
| ST-35 | Focus view can return to original size | Protected focus route/browser test | PASS |
| ST-36 | 100/250/500 live views supported | Queue size tests | PASS |

## Teacher requirements

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| TE-01 | Professional animated login | Shared commercial auth UI and responsive rendering | PASS |
| TE-02 | Create session | Integration tests | PASS |
| TE-03 | Close session | Integration/admin lifecycle tests | PASS |
| TE-04 | Reopen session | Integration/admin lifecycle tests | PASS |
| TE-05 | 90-minute duration | Session control test | PASS |
| TE-06 | 120-minute duration | Session control test | PASS |
| TE-07 | 180-minute duration | Session control test | PASS |
| TE-08 | Question limit 1–10,000,000 | Boundary/control tests | PASS |
| TE-09 | QR and link available during session | Teacher live/focus tests | PASS |
| TE-10 | Full QR mode | QR route test | PASS |
| TE-11 | Copy link | Live Chromium copy feedback test | PASS |
| TE-12 | Download QR PNG | Browser download and integration tests | PASS |
| TE-13 | Print QR | Template/UI contract | PASS |
| TE-14 | Share QR | Integration/UI contract | PASS |
| TE-15 | Return from QR/focus | Focus route controls | PASS |
| TE-16 | Live page silently refreshes every second | Template contract and browser polling test | PASS |
| TE-17 | Teacher live API hides student name | Anonymous API test | PASS |
| TE-18 | Teacher live API hides mobile | Anonymous API test | PASS |
| TE-19 | Teacher live page hides student count | UI/privacy contract | PASS |
| TE-20 | Highest-voted open doubt first | API ordering tests | PASS |
| TE-21 | Live cards hide category/keyword | Teacher privacy/render tests | PASS |
| TE-22 | Mark Completed | Lifecycle tests | PASS |
| TE-23 | Skip | Lifecycle tests | PASS |
| TE-24 | Reopen | Lifecycle tests | PASS |
| TE-25 | Attachment Download only when attachment exists | Attachment tests | PASS |
| TE-26 | No teacher reply box in doubt cards | UI contract | PASS |
| TE-27 | Completed list collapsed by default | Template/UI tests | PASS |
| TE-28 | Skipped list collapsed by default | Template/UI tests | PASS |
| TE-29 | Control question limit | Session settings tests | PASS |
| TE-30 | Control student attachment-download permission | Permission tests | PASS |
| TE-31 | Download all attachments ZIP | ZIP test | PASS |
| TE-32 | Export current session questions | CSV test | PASS |
| TE-33 | Share notes | Resource tests | PASS |
| TE-34 | Share PDF/doc/image/presentation/TXT | Resource file matrix | PASS |
| TE-35 | Share valid HTTP/HTTPS video link | URL/resource tests | PASS |
| TE-36 | Reject unsafe/non-HTTP video link | URL validation test | PASS |
| TE-37 | Automatic question bank for open/completed | Repository tests | PASS |
| TE-38 | Skipped excluded from question bank | Repository lifecycle tests | PASS |
| TE-39 | Question bank stores session/date/category/keyword/votes/status | Database/export tests | PASS |
| TE-40 | Export all/current/selected bank data | Export tests | PASS |
| TE-41 | Category/keyword/session analytics | Analytics tests | PASS |
| TE-42 | Teacher changes own password | Password test | PASS |
| TE-43 | Live panel can minimize/maximize | Chromium focus-control test | PASS |
| TE-44 | Full-screen/new-window/original-size controls | Focus route/browser tests | PASS |
| TE-45 | Two teachers have isolated sessions/data | Dedicated 1.5.0 isolation test | PASS |
| TE-46 | Teacher cannot access another teacher's session API | Ownership/isolation test | PASS |

## Administrator requirements

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| AD-01 | International admin login | Responsive auth rendering | PASS |
| AD-02 | Full platform control | Route and complete admin suite | PASS |
| AD-03 | Change own password | Admin password test | PASS |
| AD-04 | Create second admin | Admin management test | PASS |
| AD-05 | Create teacher with required fields | Teacher creation test | PASS |
| AD-06 | Optional teacher email/DOB | Creation/edit tests | PASS |
| AD-07 | Edit teacher | Admin edit test | PASS |
| AD-08 | Enable teacher | Status tests | PASS |
| AD-09 | Disable teacher | Status/auth tests | PASS |
| AD-10 | Soft-delete teacher | Status tests | PASS |
| AD-11 | Reset teacher password | Reset test | PASS |
| AD-12 | View current/past sessions | Admin page tests | PASS |
| AD-13 | Close/reopen any session | Admin lifecycle tests | PASS |
| AD-14 | View student name/mobile | Admin data tests | PASS |
| AD-15 | View/download questions | Admin export tests | PASS |
| AD-16 | Teacher/session question-bank filters/downloads | Filter/export tests | PASS |
| AD-17 | Student/session/all-question exports | Export tests | PASS |
| AD-18 | Category/keyword/teacher/status lifecycle analytics | Analytics tests | PASS |
| AD-19 | Change logo | Brand upload test | PASS |
| AD-20 | Dashboard avoids endless activity list | Compact dashboard plus paginated activity test | PASS |
| AD-21 | Tables use search/filter/pagination/page size | Admin pagination tests | PASS |

## Session, authentication, and privacy stability

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| AU-01 | Teacher and student coexist in same browser | Role-session stability test and Chromium context test | PASS |
| AU-02 | Admin login does not clear teacher/student | Role-session stability test | PASS |
| AU-03 | Teacher logout preserves student role | Role-scoped logout test | PASS |
| AU-04 | Teacher actions preserve student session | Stability test | PASS |
| AU-05 | Passwords are hashed | Auth/database tests | PASS |
| AU-06 | Valid legacy plaintext login upgrades hash | Migration/auth test | PASS |
| AU-07 | Protected routes reject wrong role | Route protection tests | PASS |
| AU-08 | Teacher ownership enforced | Ownership tests | PASS |

## Engineering and operations

| ID | Requirement | Implementation/evidence | Status |
|---|---|---|---:|
| EN-01 | Existing data migrated without deleting records | Migration tests | PASS |
| EN-02 | SQLite WAL for laptop build | PRAGMA test | PASS |
| EN-03 | Unique vote enforcement | Database index and behavior tests | PASS |
| EN-04 | Repository uniqueness/indexes | Database index tests | PASS |
| EN-05 | Waitress server support | Requirements/start scripts/Docker contracts | PASS |
| EN-06 | Health endpoint | `/healthz` test | PASS |
| EN-07 | Environment-based port/debug/cookie paths | Configuration test | PASS |
| EN-08 | Response security headers | Header test | PASS |
| EN-09 | API responses not cached | Header test | PASS |
| EN-10 | Python source compiles | Compile gate | PASS |
| EN-11 | All Jinja templates parse | 34-template parse gate | PASS |
| EN-12 | JavaScript parses | Node syntax gate | PASS |
| EN-13 | CSS parses | 978-rule parser gate | PASS |
| EN-14 | Compose/workflow YAML parses | YAML gate | PASS |
| EN-15 | Complete automated Python suite | 57 tests | PASS |
| EN-16 | 12-device matrix | 132/132 checks | PASS |
| EN-17 | Chromium live browser tests | 31 passed across groups | PASS |
| EN-18 | Firefox live browser tests | CI configured; local binary unavailable | NOT RUN |
| EN-19 | WebKit/Safari live browser tests | CI configured; local binary unavailable | NOT RUN |
| EN-20 | Docker production build | Files/contracts pass; Docker CLI unavailable | NOT RUN |
| EN-21 | Docker health smoke | CI configured; Docker CLI unavailable | NOT RUN |
| EN-22 | GitHub Actions core execution | Workflow configured; repository push required | NOT RUN |
| EN-23 | GitHub Actions browser execution | Workflow configured; repository push required | NOT RUN |
| EN-24 | GHCR publish | Workflow configured; successful push/tag required | NOT RUN |
| EN-25 | Physical Android Chrome acceptance | Responsive Chromium profiles pass; physical lab required | NOT RUN |
| EN-26 | Physical iPhone/iPad Safari acceptance | Responsive profiles pass; physical WebKit lab required | NOT RUN |
| EN-27 | Penetration test | Independent assessment required | NOT RUN |
| EN-28 | 50M-student load test | Current SQLite build is not intended for this scale | NOT RUN |
| EN-29 | Packaged ZIP integrity and clean extraction | SHA-256 manifest plus extracted 57-test suite | PASS |

## Final requirement status

- Functional and source-contract requirements executed locally: **PASS**.
- Chromium and 12-profile responsive scope: **PASS**.
- Docker runtime, Firefox, WebKit/Safari, hosted CI, physical devices, penetration, and very-large-scale load: **NOT RUN locally** and must be completed before a commercial production launch.
