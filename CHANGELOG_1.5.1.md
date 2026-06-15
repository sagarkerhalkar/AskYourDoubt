# Changelog

## 1.5.1 — Session-wise Question Bank and Commercial SaaS Correction

### Fixed

- Teacher Question Bank session selector now changes the visible question list instead of acting only as an export selector.
- Session filter ownership is validated so one teacher cannot filter or export another teacher's session.
- Status filters, pagination, selected-session context, current-view export, and full-session export work together.
- Student file selection now clearly shows filename, size, upload-ready state, and removal control.
- Completed question text remains visible in Teacher history and Student Answered.
- Teacher and Student Resources use consistent clean card layouts and explicit file/video/note actions.
- Replaced violet/orange role-page decoration with a restrained navy/blue/teal commercial palette.
- Added local realistic product-scene SVG assets and lightweight motion with reduced-motion support.

### QA

- Added dedicated 1.5.1 regression tests for session-wise question filtering, cross-teacher isolation, attachment feedback, completed-question visibility, and resource workflows.
- Core suite: 62 passed.
- Responsive offline Chromium matrix: 168/168 checks across 12 profiles and 14 pages.
- Live Chromium navigation in this execution environment: NOT RUN because Chromium returned `ERR_BLOCKED_BY_ADMINISTRATOR` for localhost; CI remains configured for Chromium, Firefox, and WebKit.
