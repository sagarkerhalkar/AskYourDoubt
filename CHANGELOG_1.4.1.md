# AskYourDoubt 1.4.1

- Fixed teacher/student/admin sessions logging each other out when used in different tabs or windows of one browser.
- Replaced global `session.clear()` with role-scoped session cleanup.
- Added regression tests for simultaneous teacher/student/admin use and role-scoped logout.
- Added explicit same-origin credentials to realtime and action fetch requests.
- Redesigned teacher login and student join pages.
- Reworked the teacher live-session header into a compact premium command header.
- Preserved live polling, voting, Complete, Skip, Reopen, QR, resources, attachments, pagination, exports, and admin logic.
