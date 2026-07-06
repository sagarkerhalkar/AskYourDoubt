# AskYourDoubt 1.5.1 Requirement Traceability

This table maps the user-requested corrections to implementation and executed evidence. **PASS** means executed locally. **NOT RUN** means the environment could not execute that category.

| ID | Requirement | Implementation | Evidence | Result |
|---|---|---|---|---:|
| UI-01 | Reduce oversized headings everywhere | Global role-page heading hierarchy, compact page headers and card typography in `static/css/app.css` | Core UI contracts; responsive screenshots | **PASS** |
| UI-02 | Reduce Teacher and Student top boxes | Compact Teacher command hero and Student welcome panel | 168 responsive checks; phone/tablet/laptop screenshots | **PASS** |
| UI-03 | Professional international SaaS palette | Navy sidebar, restrained blue/teal actions, white/neutral surfaces; dark violet role-page banner removed | Teacher live, question bank, resources and student screenshots | **PASS** |
| UI-04 | Realistic lightweight 3D/motion | Local product-scene SVGs, subtle perspective/float, live pulses, reduced-motion handling | CSS parse; responsive render | **PASS** |
| UI-05 | No gaming/toy-style excessive effects | Role pages use controlled shadows, small motion and semantic status accents | Visual evidence | **PASS** |
| QB-01 | Teacher sees questions session by session | `session_id` filters visible repository rows in `teacher.question_bank` | `test_v151_session_question_bank.py` | **PASS** |
| QB-02 | Session filter persists with All/Open/Completed | Status links carry selected session; pagination preserves query filters | Core tests and rendered question-bank screenshot | **PASS** |
| QB-03 | Session selector must not be export-only | Selector submits to Question Bank view; export is a separate action | Template and regression test | **PASS** |
| QB-04 | Teacher cannot access another teacher's session | Session ownership validation before filtering/exporting | Cross-teacher regression test | **PASS** |
| QB-05 | Current-view and full-session exports are distinct | Separate `Export current view` and `Export full session` actions | Core tests and screenshot | **PASS** |
| ST-01 | Student knows whether a file is attached | Selected-file panel shows filename, size, ready state and Remove button | Attachment regression test | **PASS** |
| ST-02 | Successful upload confirms filename | Submission flash includes the exact attachment filename | Attachment regression test | **PASS** |
| ST-03 | Text remains compulsory and file optional | Existing server validation preserved | Existing functional suite | **PASS** |
| ST-04 | Video doubt uploads rejected | Existing file whitelist preserved | Existing functional suite | **PASS** |
| CQ-01 | Completed question text visible to Teacher | Completed API response and Teacher history card render question text | Completed visibility regression test | **PASS** |
| CQ-02 | Completed question text visible to Student | Student Answered renderer displays full question text | Completed visibility regression test and screenshot | **PASS** |
| RS-01 | Teacher Resources looks clean and structured | Separate File, Video and Note workflows with consistent cards | Resource regression test and screenshot | **PASS** |
| RS-02 | Student Resources looks clean and readable | Commercial resource grid with type, title, note and open action | Resource regression test and screenshot | **PASS** |
| LIVE-01 | Teacher Live Doubts minimize/maximize | Minimize state and full-screen controls in shared JavaScript | Existing functional/UI suite | **PASS** |
| LIVE-02 | Student Live Doubts minimize/maximize | Minimize, maximize, new window and return controls | Existing functional/UI suite | **PASS** |
| LIVE-03 | Silent one-second Teacher refresh | In-flight guard, no-store fetch, signature comparison and 1000 ms interval | Existing functional/UI suite | **PASS** |
| LIVE-04 | Silent one-second Student refresh | In-flight guard, no-store fetch, signature comparison and 1000 ms interval | Existing functional/UI suite | **PASS** |
| LIVE-05 | Polling must not clear typed question | Ask composer is not rerendered by background polling | Existing functional/browser contract | **PASS** |
| LOGIC-01 | Separate teacher sessions | All session queries include teacher ownership | Existing isolation suite | **PASS** |
| LOGIC-02 | Separate students by session | Student membership and session checks preserved | Existing isolation suite | **PASS** |
| LOGIC-03 | Own-question voting blocked | Existing API validation preserved | Existing functional suite | **PASS** |
| LOGIC-04 | One same-doubt vote per student | Unique vote constraint and duplicate response preserved | Existing functional suite | **PASS** |
| LOGIC-05 | Complete, skip and reopen lifecycle | Doubt and repository synchronization preserved | Existing functional suite | **PASS** |
| LOGIC-06 | QR copy/download/share/print | Existing routes and controls preserved | Existing functional suite | **PASS** |
| LOGIC-07 | Admin, analytics and exports preserved | Existing routes and tests remain | Full core suite | **PASS** |
| DEV-01 | 320×568 through 2560×1440 responsive | 12 profiles × 14 pages | 168/168 Playwright offline-render checks | **PASS** |
| DEV-02 | Question Bank and Resources included in responsive matrix | Added Teacher Question Bank, Teacher Resources, Student Answered and Student Resources | 24 screenshots | **PASS** |
| BR-01 | Chromium live browser tests | Test suite invoked, but localhost blocked by environment policy | 31 explicit skips | **NOT RUN** |
| BR-02 | Firefox browser tests | Configured in CI; binary unavailable locally | Workflow source and report | **NOT RUN** |
| BR-03 | WebKit/Safari tests | Configured in CI; binary unavailable locally | Workflow source and report | **NOT RUN** |
| QA-01 | Compile every Python module | `compileall` | Static evidence | **PASS** |
| QA-02 | Test every route/function requirement | 62 integration and requirement tests | JUnit and output | **PASS** |
| QA-03 | Parse all Jinja templates | 34 templates parsed | Static evidence | **PASS** |
| QA-04 | Validate JavaScript syntax | Node syntax check | Static evidence | **PASS** |
| QA-05 | Validate CSS | 1,218 rules, zero parse errors | Static evidence | **PASS** |
| QA-06 | Validate CI/CD YAML | Compose and workflows parsed | Static evidence | **PASS** |
| QA-07 | Native production-like smoke | Waitress `/healthz` and home HTTP 200 | Smoke evidence | **PASS** |
| QA-08 | Docker image/container smoke | Docker CLI unavailable locally | Test report | **NOT RUN** |
| QA-09 | Hosted GitHub Actions | Requires repository push | Test report | **NOT RUN** |

## Evidence locations

```text
TEST_REPORT_1.5.1.md
test_evidence_1_5_1/core/
test_evidence_1_5_1/static/
test_evidence_1_5_1/browser/
test_evidence_1_5_1/device/
```
