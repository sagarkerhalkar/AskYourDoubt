# Changelog

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
