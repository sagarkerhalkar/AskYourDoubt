# AskYourDoubt 1.4.1 Test Report

## Root cause fixed

Teacher, student, and admin used the same Flask session cookie. Login and logout routes called `session.clear()`, so opening a student session in another tab removed the teacher identity, and teacher/admin login removed the student identity. This caused the apparent automatic logout after a question or action.

Version 1.4.1 uses role-scoped cleanup:

- teacher login/logout changes only teacher keys;
- student join/logout changes only student keys;
- admin login/logout changes only admin keys.

Teacher, student, and admin can now coexist in different tabs/windows of one browser.

## Tests actually executed

```text
Python compilation: PASS
Flask integration/UI tests: 41 PASS
Same-browser teacher + student coexistence: PASS
Student question submission retains teacher login: PASS
Teacher Complete action retains student login: PASS
Role-scoped teacher logout: PASS
Role-scoped student logout: PASS
Admin login retains teacher/student sessions: PASS
Responsive Chromium offline renders: 132/132 PASS
Device profiles: 12
Pages per profile: 11
Screenshots: 24
```

## Live browser status in this build environment

```text
Chromium live localhost navigation: BLOCKED BY ENVIRONMENT (ERR_BLOCKED_BY_ADMINISTRATOR)
Firefox: NOT RUN HERE
WebKit: NOT RUN HERE
```

Run `RUN_FULL_QA_1_4_1.bat` on the Windows laptop. Only claim full browser success when it prints `FULL QA PASSED ON THIS MACHINE.`

## Visual changes

- Redesigned teacher login.
- Redesigned student session check-in.
- Reworked teacher live-session top area into a compact command header.
- Retained Full Screen, New Window, QR/link side panel, Copy Link, Download QR, Share QR, Print QR, resources, question actions, and pagination.
