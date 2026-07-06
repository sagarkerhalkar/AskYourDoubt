# Read First — Version 1.4

This release implements the requested work rather than only documenting it.

## Added

- Teacher Dashboard redesign.
- Teacher Live Doubts redesign.
- Student portal and Live Doubts redesign.
- Teacher Live Doubts browser full-screen mode.
- Teacher Live Doubts dedicated new-window focus mode.
- Student Live Doubts browser full-screen mode.
- Student Live Doubts dedicated new-window focus mode.
- Return to Original Size for teacher and student.
- Teacher right-side QR/join panel in immersive mode.
- Copy Link, Download QR, Share QR, and Print QR in immersive mode.
- Existing live polling, voting, complete, skip, reopen, downloads, resources, question limits, question bank, analytics, exports, passwords, and admin logic retained.

## Install

```text
INSTALL_GLOBAL_REBUILD_1_4.bat
```

## Test

```text
RUN_FULL_QA_1_4.bat
```

## Actual packaged evidence

```text
37 core tests passed
132/132 responsive Chromium checks passed
24 screenshots generated
56 Flask routes registered
```

Live Chromium/Firefox/WebKit interaction testing must be completed on the Windows laptop or GitHub Actions because localhost browser navigation was blocked in the packaging environment.
