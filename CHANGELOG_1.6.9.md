# AskYourDoubt v1.6.9 — Session Duration 0 Seconds to 24 Hours

## Changed
- Teacher session creation no longer uses fixed 90/120/180 minute dropdown.
- Teacher can enter any session duration in seconds from `0` to `86400`.
- `0` seconds means manual close/no automatic expiry.
- Teacher can update the duration from the live session control panel.
- Reopen respects the saved precise duration.
- Added `duration_seconds` database column while keeping legacy `duration` column for compatibility.

## UI
- Create Session page now has a mobile/browser-friendly numeric duration field.
- Added quick duration preset buttons: Manual, 1 hr, 90 min, 2 hr, 24 hr.
- Countdown display safely shows `Manual close` when no automatic expiry is set.

## Compatibility
- Old forms/tests that still post legacy `duration` in minutes continue to work.
- New forms post `duration_seconds` for precise seconds-level control.

## Security / Privacy
- No change to teacher privacy rules. Teacher still cannot see student name, mobile, joined count, or joined list.
