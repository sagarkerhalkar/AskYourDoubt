# PROJECT_CONVERSATION_LOG.md


## 1.6.8 — Privacy audit and AWS public deployment planning (2026-06-27)

User marked current source as working and asked to verify that teachers cannot see student details:
student name, mobile number, and joined-student count. User also asked for public AWS deployment planning for 10,000,000 students.

Actions:
- Audited teacher-facing API, teacher templates, teacher question-bank, CSV exports, and resource downloads.
- Found and fixed a privacy edge case where teacher downloads could expose the original student-uploaded filename.
- Added automated test that verifies teacher API/downloads do not expose student identity or original filenames.
- Added AWS 10M deployment plan. Current SQLite/local-filesystem build is not suitable for direct 10M deployment; requires PostgreSQL/Aurora, S3, Redis, CDN/WAF, ECS/Fargate/ALB, queue workers, and WebSocket/SSE architecture.
- Kept admin-only access to student name/mobile.


## 2026-07-05 — v1.6.9 Session Duration Control
- User requested only one code change: teachers must create sessions with any duration from 0 seconds to maximum 24 hours, not only fixed 90/120/180 minute choices.
- Implemented precise `duration_seconds` control in teacher session creation and live session settings.
- Range is enforced server-side: 0 to 86,400 seconds. 0 means manual close/no automatic expiry.
- Kept legacy `duration` minutes field for older data/tests and added `duration_seconds` for precise seconds.
- Added responsive/mobile-safe numeric inputs and quick presets: Manual, 1 hr, 90 min, 2 hr, 24 hr.
- Re-tested core app, privacy-sensitive flows, and browser matrix availability.

## 2026-07-05 - v1.6.10 duration hours + professional session controls
User requested only one focused change: teacher session creation and live control duration must be in hours format, not raw seconds or fixed 90/120/180 minute choices. Required examples: `.30` for 30 minutes, `1.30` for 90 minutes, `0` manual, max 24 hours. User also said the “Session controls / Doubt Control Center / Upload Resources / Download ZIP / Export Questions” area looked ugly and must be made professional without touching remaining logic. Implemented new `duration_hours` UI field and backend parser while keeping old `duration_seconds` compatibility. Restyled only the control area and added tests/device responsive evidence.
