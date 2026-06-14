# Product Requirements — Ask Your Doubt

## Product goal

Ask Your Doubt must be a commercial, global, international-level live classroom platform with next-generation UI/UX, animation, automation, responsive layouts, role privacy, realtime question ranking, analytics, exports, and production migration readiness.

## Design requirements

- Product name: Ask Your Doubt.
- Theme: black, green, white, orange, yellow, with cyan accents.
- Font sizes must remain balanced and readable.
- Commercial home page suitable for product sales and demonstrations.
- Professional photographic student/teacher/admin visuals, not cartoon-only pages.
- 3D-style depth, subtle animated motion, animated analytics, hover and touch feedback.
- Mobile-first responsive layouts for Android and iOS.
- Tablet, laptop, and desktop responsive layouts.
- Chrome/Chromium, Firefox, and WebKit/Safari CI browser matrix.
- Accessibility reduced-motion support.
- High-resolution replaceable logo.
- No visible realtime page-refresh flicker.

## Student requirements

- Join using QR link or teacher-provided link/session code.
- Full name required.
- Mobile required, exactly 10 numeric digits.
- Student pages do not expose teacher/admin portal navigation.
- Closed session shows a dedicated closed-session message.
- Question text compulsory.
- WhatsApp-style writing experience with emojis.
- Optional file upload, maximum 10 MB.
- Allowed: PDF, Word, TXT, and images.
- Student video upload prohibited.
- “My Question” marker.
- Student cannot vote own question.
- Another student can vote once using “I have the same doubt”.
- Vote count increases and controls teacher ranking.
- Open doubts update silently every second.
- Highest-voted doubts appear first.
- Skipped doubts are never shown to students.
- Completed doubts move to a collapsible Answered section.
- Other student attachments remain hidden unless teacher enables downloads.
- Download button appears only when allowed and a file exists.
- Teacher resources are directly available without extra student permission.
- Session name displayed at medium scale.
- Countdown displayed.
- After question submission, automatically go to Live Doubts.
- Selected tab stays selected after refresh.

## Teacher requirements

- Professional animated login page.
- Create, close, and reopen sessions.
- Session durations: 90, 120, 180 minutes.
- Per-student question limit: 1 to 10,000,000.
- Session QR and link remain available throughout the session.
- Full-screen QR mode, copy link, download QR, print QR, return to session.
- Teacher live page updates silently every second.
- Teacher cannot see student name, mobile, or student count in the live session.
- Highest-voted open doubt appears first.
- Live doubt cards do not show category or keyword.
- Actions: Mark Completed, Skip, Reopen.
- Attachment Download button only when attachment exists.
- Teacher does not type replies in doubt cards.
- Completed and skipped lists collapsed by default.
- Doubt Control Center:
  - Question limit.
  - Student attachment-download permission.
  - All attachment ZIP.
  - Current session question CSV.
- Share resources: notes, PDFs, documents, images, presentations, video links.
- Automatic question bank for open and completed doubts.
- Skipped doubts excluded from question bank.
- Question bank stores session, date, category, keyword/topic, votes, status.
- Download current session, all sessions, all question-bank items, selected session question bank.
- Animated category, keyword/topic, and session analytics.
- Teacher changes own password.

## Admin requirements

- International admin login page.
- Full platform control.
- Change own password.
- Create second administrators.
- Create teacher with required name, mobile, username, password.
- Teacher email and date of birth optional.
- Edit teacher profile.
- Enable, disable, soft-delete teacher.
- Reset teacher password.
- View all current and past sessions.
- Close and reopen any session.
- View student name and mobile.
- View and download all questions.
- Teacher-wise and session-wise question-bank filters/downloads.
- All-question, student, and session exports.
- Category, keyword, teacher, status, skipped, completed, and open analytics.
- Change high-resolution logo.

## Engineering requirements

- Existing data migration without deleting records.
- Password hashing with legacy plaintext upgrade after valid login.
- File type and 10 MB server-side enforcement.
- Unique student vote enforcement.
- Teacher ownership checks.
- Role-based route protection.
- SQLite WAL for laptop testing.
- Waitress production-like Windows serving.
- Automated Python integration tests.
- GitHub Actions Python CI.
- GitHub Actions Chromium/Firefox/WebKit responsive matrix.
- Detailed README, test report, production scale plan, and handoff.

## Scale requirement

Target vision: 50,000,000 students.

The current laptop build validates product behaviour and UI. Production capacity at that scale requires the architecture in `PRODUCTION_SCALE_PLAN.md`.
