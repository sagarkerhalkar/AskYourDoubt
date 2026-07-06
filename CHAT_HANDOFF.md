# AskYourDoubt Complete Chat Handoff — Current 1.3 Direction

## Continue from

```text
D:\AskYourDoubtGlobal
AskYourDoubt Global Rebuild 1.3 Light 3D
```

Do not start from scratch. Do not replace the working project with another response-wrapper UI patch.

## Preserve

- database.db
- uploads
- teacher resources
- generated QR files
- exports
- uploaded logo
- all working routes
- student/teacher/admin permissions
- vote logic
- live APIs
- complete/skip/reopen logic
- password logic

## Immediate visual requirements

- Admin dashboard must not become endless.
- Dashboard shows latest five activities.
- Full activity page uses 10/20/30 pagination.
- Teacher live page must be light, attractive, animated, and 3D.
- Student live page must receive the same premium treatment.
- Session title must remain compact.
- Open Doubts are the main focus.
- Silent realtime updates.
- No visible refresh flicker.
- Top 100 default and top 500 option.
- Standard pages use 10/20/30 pagination.
- Global neutral colors, not dark-green dominance.
- Balanced international typography.
- Mobile, iPhone, iPad, Android, laptop, desktop, Chromium, Firefox, and WebKit testing.

## Teacher QR requirements

- Copy join link.
- Full-screen QR.
- Download QR PNG.
- Share QR.
- Print QR.
- Return to original session layout.
- Ownership-protected QR download route.

## Test-reporting rule

Report every category as:

```text
PASS
FAIL
NOT RUN
```

Never claim a browser/device passed when it did not actually run.

## Product attribution

```text
Built by Sagar Kerhalkar × ChatGPT
```


## 1.6.8 — Privacy audit and AWS public deployment planning (2026-06-27)

User marked current source as working and asked to verify that teachers cannot see student details:
student name, mobile number, and joined-student count. User also asked for public AWS deployment planning for 10,000,000 students.

Actions:
- Audited teacher-facing API, teacher templates, teacher question-bank, CSV exports, and resource downloads.
- Found and fixed a privacy edge case where teacher downloads could expose the original student-uploaded filename.
- Added automated test that verifies teacher API/downloads do not expose student identity or original filenames.
- Added AWS 10M deployment plan. Current SQLite/local-filesystem build is not suitable for direct 10M deployment; requires PostgreSQL/Aurora, S3, Redis, CDN/WAF, ECS/Fargate/ALB, queue workers, and WebSocket/SSE architecture.
- Kept admin-only access to student name/mobile.


## Latest handoff — v1.6.9
User requested one focused change: teacher session duration must be any value from 0 seconds to 24 hours, not fixed 90/120/180 minutes. Implemented `duration_seconds` with server-side clamp 0–86400. 0 means manual close/no automatic expiry. Create-session UI now uses numeric seconds input with presets. Live session settings can update duration. Tests passed: 71 functional tests. Browser tests are included but skipped in this sandbox due local browser navigation policy.

## Handoff update - v1.6.10
Current locked behavior: session duration is entered as hours-style text. Examples: `0` manual, `.30` = 30 minutes, `1.30` = 90 minutes, `24` = max 24 hours. Backend stores seconds in `duration_seconds` as before. Teacher/admin privacy and core session logic are unchanged. Live session controls are now styled with `.teacher-control-card-pro`. Continue to preserve responsive/mobile/Apple/browser compatibility and run compile, pytest, device matrix, and browser matrix where available.
