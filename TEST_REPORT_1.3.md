# AskYourDoubt 1.3 Test Report

## Executed successfully in the build environment

- Dependency resolution dry-run: PASS
- Python compile: PASS
- Flask integration/UI tests: 33 PASS
- QR download route test: PASS
- QR ownership/access-control test: PASS
- QR share UI/JavaScript contract test: PASS
- Admin latest-five activity test: PASS
- Admin activity pagination test: PASS
- 12 viewport profiles × 9 pages: 108 responsive checks PASS
- Representative screenshots: 15 generated

## Viewports checked

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

## Live browser matrix in this environment

- Chromium live localhost navigation: NOT RUN successfully
- Firefox live localhost navigation: NOT RUN
- WebKit live localhost navigation: NOT RUN

Reason: the sandbox browser blocked localhost navigation with `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
This is an environment restriction, not a claimed application pass.

Use `RUN_FULL_QA_1_3.bat` on the Windows laptop for the real Chromium, Firefox, and WebKit result.
