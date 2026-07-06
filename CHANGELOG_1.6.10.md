# AskYourDoubt v1.6.10 - Hours Duration & Professional Session Controls

## Locked requirement
Only the teacher session duration and the live-session controls UI were changed. Existing privacy/session logic was not touched.

## Changes
- Teacher session duration now uses easy hours format in the UI:
  - `0` = manual close / no auto-expiry
  - `.30` = 30 minutes
  - `1` = 1 hour
  - `1.30` = 1 hour 30 minutes / 90 minutes
  - `12` = 12 hours
  - `24` = maximum 24 hours
- Backend accepts the new `duration_hours` field and converts it to seconds safely.
- Backward compatibility preserved for existing `duration_seconds` tests/forms.
- Live session “Doubt Control Center” redesigned to a cleaner professional control card.
- Student doubt limit quick presets improved: 1, 100, 1 lakh, 1 crore.
- Resource actions retained and restyled: Upload Resources, Download ZIP, Export Questions.
- Mobile/tablet/laptop/browser responsive CSS added for the control area, including iPhone/Safari input-size safety.

## Not changed
- Teacher privacy rules.
- Student/admin data visibility rules.
- Doubt submission/voting/session logic.
- QR/link logic.
- Exports/resource endpoints.
