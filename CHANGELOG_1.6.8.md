# Changelog 1.6.8 — Privacy Audit + AWS 10M Readiness

Date: 2026-06-27

## Added
- Teacher privacy audit report: `PRIVACY_AUDIT_1.6.8.md`
- AWS public deployment and 10M-student scaling plan: `AWS_PUBLIC_DEPLOYMENT_PLAN_10M.md`
- Test report: `TEST_REPORT_1.6.8.md`
- Backup before patch: `backups/v1_6_8_pre_patch_privacy_aws_20260622_1830/`

## Fixed
- Teacher single student-resource attachment downloads no longer expose original uploaded filenames.
- Teacher student-attachments ZIP no longer exposes original uploaded filenames.
- Anonymous teacher-facing filenames now use:
  `student_resource_doubt_<id>.<ext>`

## Confirmed
- Teacher live API does not return student name/mobile/joined-count data.
- Teacher live UI consumes only anonymous question data.
- Teacher question-bank CSV contains question data only.
- Admin remains the only role allowed to see student identity and mobile data.
