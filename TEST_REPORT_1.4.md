# AskYourDoubt 1.4 Test Report

## Result summary

| Gate | Result |
|---|---|
| Python compile | PASS |
| Flask route registration | PASS — 56 routes |
| Core integration and UI contracts | PASS — 37 tests |
| Responsive Chromium render matrix | PASS — 132/132 |
| Responsive failures | 0 |
| Generated evidence screenshots | 24 |
| Live Chromium localhost interaction matrix | NOT RUN — blocked by restricted environment |
| Firefox live matrix | NOT RUN in packaging environment |
| WebKit live matrix | NOT RUN in packaging environment |

## Tested v1.4 functions

- Teacher focus route authorization.
- Student focus route authorization.
- Teacher QR/link actions in focus mode.
- Teacher Dashboard Live Focus link.
- Teacher and student Top 100/250/500 controls.
- Return-to-original-size controls.
- Existing student/teacher/admin regression suite.
- Responsive behavior for normal and immersive pages.

## Responsive viewports

`320x568`, `360x800`, `390x844`, `412x915`, `768x1024`, `820x1180`, `1024x1366`, `1280x800`, `1366x768`, `1440x900`, `1920x1080`, `2560x1440`.

## Evidence limitation

The browser runtime in the packaging environment returned `ERR_BLOCKED_BY_ADMINISTRATOR` for localhost live navigation. This report does not claim live Chromium, Firefox, or WebKit success. Run `RUN_FULL_QA_1_4.bat` on Windows or use GitHub Actions.
