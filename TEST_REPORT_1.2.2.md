# AskYourDoubt 1.2.2 — Test Report

## Executed in the build environment

- Python compile/import: PASS
- Pytest integration and UI contracts: **29 passed**
- Responsive Chromium offline render matrix: **108 passed, 0 failed**
- Device profiles: 12
- Pages per profile: 9
- Screenshots: 15
- Windows locked-output fallback logic: PASS (forced locked/unwritable output test successfully moved evidence to a temporary timestamped folder)

## Responsive profiles

- 320×568
- 360×800
- 390×844
- 412×915
- 768×1024
- 820×1180
- 1024×1366
- 1280×800
- 1366×768
- 1440×900
- 1920×1080
- 2560×1440

## Functional contracts covered

- Live doubts default 100
- Live doubts optional 250/500
- Live pagination
- Standard 10/20/30 pagination
- Student/teacher live background polling
- Copy Link control
- Teacher resource controls
- Student voting, self-vote prevention, and duplicate-vote prevention
- Question limit
- Attachment behavior
- Session lifecycle
- Question bank lifecycle
- Admin/teacher/student route contracts
- Mobile/tablet/desktop breakpoints
- Premium animation and 3D CSS/JavaScript contracts

## Not claimed as passed here

The full live Playwright navigation suite for Chromium, Firefox, and WebKit could not run in the restricted build environment because browser navigation to localhost was blocked. Run `RUN_FULL_QA_1_2_2.bat` on the Windows laptop. Only claim those browsers PASS when that script completes successfully.
