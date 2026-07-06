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
