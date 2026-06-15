# AskYourDoubt Changelog

## 1.5.2 — Sky-Blue SaaS UI, Pagination, Session Exports and QR Focus

### Visual system

- Replaced green/teal-led branding with navy, sky-blue, white and cool-grey surfaces.
- Replaced coloured emoji navigation markers with neutral symbols.
- Added a local realistic Indian classroom image to the Teacher Login page.
- Preserved compact professional typography, restrained 3D depth and reduced-motion support.

### Teacher live session

- Added independent pagination for Completed Questions: 10, 20 or 30 per page.
- Added independent pagination for Skipped Doubts: 10, 20 or 30 per page.
- Added current-session downloads for:
  - Total Questions: Open + Completed
  - Open
  - Completed
  - Skipped
- Added a dedicated Skipped metric while retaining total votes.
- Defined Total Questions as Open + Completed; Skipped remains separate.
- Added QR/link browser-fullscreen control.
- Retained the dedicated Full Page QR view with Back to Session.

### Student portal

- Added independent pagination to Answered Questions: 10, 20 or 30 per page.
- Preserved visible completed-question text, attachment links, silent one-second updates and file-selection feedback.

### Backend and QA

- Added API pagination metadata for teacher completed/skipped lists and student answered lists.
- Added filtered current-session CSV export logic with teacher ownership protection.
- Added 1.5.2 regression tests for pagination, filtered exports, palette contract and login image.
- Core suite: 66 passed.
- Responsive matrix: 168/168 passed across 12 device profiles and 14 pages per profile.

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

## 1.5.0 — Commercial Global UI, Silent Live Focus, and Full QA

### Added

- Commercial international SaaS design layer across public, student, teacher, and admin experiences.
- Compact global typography hierarchy and reduced hero/header heights.
- Student and teacher live-panel minimize/maximize controls.
- Full-screen browser mode, simulated full-screen fallback, dedicated live window, and return-to-original-size controls.
- Silent one-second teacher and student polling with in-flight guards, no-store requests, change signatures, and visibility recovery.
- Stable copy-link feedback with clipboard and manual-copy fallback.
- `/healthz` endpoint and security/cache response headers.
- Environment-driven port, debug, secure-cookie, data, upload, QR, and export settings.
- Non-root Docker image, Docker test image, local Compose, production Compose, and Caddy HTTPS example.
- Python 3.11–3.14 core CI matrix.
- Chromium, Firefox, and WebKit CI jobs, Docker smoke, and GHCR publishing.
- Complete 1.5.0 requirement suite and requirement traceability document.

### Redesigned

- All oversized headings, page titles, card headings, form titles, and hero typography.
- Teacher dashboard and teacher live command area.
- Student welcome and live classroom flow.
- Mobile, tablet, laptop, MacBook, Full HD, and QHD spacing.
- Color system to professional navy, blue, teal, white, and neutral surfaces with controlled accents.

### Preserved and regression-tested

- Teacher-specific session isolation.
- Student-specific session membership.
- Role coexistence in the same browser.
- Question submission, limits, attachments, and emoji text.
- No self-vote and one same-doubt vote per student.
- Vote-ranked live queue.
- Complete, skip, reopen lifecycle.
- QR link, QR download, QR sharing, and printing.
- Resource files, notes, and video links.
- Question bank, analytics, exports, passwords, and admin management.

### Engineering fixes

- Removed external Google Font requests to improve offline loading, privacy, and browser-test stability.
- Request envelope permits multipart overhead while the actual file remains limited to 10 MB.
- Video links accept only valid HTTP/HTTPS URLs.
- API responses use `Cache-Control: no-store`.
- Quality-gate PowerShell Python invocation and route threshold corrected.

## 1.4.1 — Role Session Stability

- Teacher, student, and administrator identities can coexist in separate tabs/windows.
- Role login/logout no longer clears unrelated role state.
- Teacher actions no longer remove the student session.

## 1.4 — Immersive Live Experience

- Protected teacher and student focus routes.
- Fullscreen API controls and responsive fixed-layout fallback.
- Return-to-original-size and new-window actions.
- Teacher immersive QR rail and live focus.
