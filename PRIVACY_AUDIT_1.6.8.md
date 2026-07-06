# AskYourDoubt Privacy Audit 1.6.8

Date: 2026-06-27

## User requirement checked

Teacher must not see:
- Student name
- Student mobile number
- How many students joined the current session
- Student identity in live doubt API, teacher UI, teacher CSV exports, or teacher resource downloads

Admin may see student identity and mobile number.

## Audit result

Status: **PASS after privacy hardening patch**

### Checked teacher-facing surfaces

1. `/api/teacher/session/<session_id>`
   - Returns only session metadata, question text, vote count, status, created time, attachment presence, and anonymous download URL.
   - Does **not** return `student_name`, `student_mobile`, `mobile`, `joined`, `student_count`, or `session_students`.

2. Teacher live session page
   - Uses only the teacher API payload.
   - Shows questions and votes only.
   - Does **not** render student name/mobile/joined count.

3. Teacher question bank
   - Uses the `repository` table.
   - Exports only question/category/keyword/votes/status/session.
   - Does **not** export student name/mobile.

4. Teacher question CSV exports
   - Exports question data only.
   - Does **not** include student name/mobile.

5. Teacher student-resource downloads
   - Hardened in 1.6.8.
   - Single student attachment download now uses anonymous filename:
     `student_resource_doubt_<id>.<ext>`
   - ZIP student attachment names now use anonymous filenames.
   - Original student-uploaded filenames are no longer exposed to teachers.

## Important finding before patch

The current working source already hid student names/mobiles from teacher live API and question-bank CSV, but teacher attachment downloads used the original uploaded filename. If a student uploaded a file named with their name/mobile number, that filename could expose identity to the teacher.

This is now fixed in:
- `routes/teacher.py`
- `tests/test_student_teacher_flow.py`

## Automated privacy test added

Added test:
`test_teacher_never_receives_student_identity_or_original_attachment_filename`

It verifies:
- Teacher API payload does not contain student name/mobile/joined-count terms.
- Teacher single attachment download does not contain original student filename.
- Teacher ZIP download does not contain original student filename.

## Current limits

This privacy audit confirms teacher-facing identity isolation. It does not make the current SQLite-based app ready for 10,000,000 public students. See `AWS_PUBLIC_DEPLOYMENT_PLAN_10M.md`.
