# AskYourDoubt Global Rebuild 1.3 — Light 3D Experience

This update directly redesigns the real admin dashboard and teacher live-session templates. It does not use an after-response HTML wrapper.

## Main changes

### Admin dashboard

- Teacher Activity on the home dashboard is limited to the latest five items.
- A new `/admin/activity` page shows full activity with 10/20/30 rows-per-page pagination.
- Compact seven-card metrics.
- Five recent sessions only on the dashboard.
- Light international SaaS palette.
- 3D cap illustration, card motion, keyword cloud, analytics bars, and quick actions.

### Teacher live session

- Complete light premium redesign.
- Medium session title and compact controls.
- Animated 3D teacher scene and live microphone visual.
- Highest-voted doubts first.
- Silent one-second updates remain unchanged.
- No student name, mobile, category, or keyword shown in the teacher live queue.
- Mark Completed, Skip, Reopen, and attachment Download logic preserved.
- Top 100 / 250 / 500 live-list control preserved.
- Completed and skipped doubts remain collapsed.
- Doubt Control Center preserves question limit, download permission, resources, ZIP, and CSV.

### QR download and sharing

Teacher can now:

- copy the join link
- download the QR as a PNG attachment
- share the QR using the mobile/tablet native share sheet
- share only the session link where file sharing is unavailable
- use a fallback that downloads the QR and copies the join link
- open QR full screen
- print QR

New protected route:

```text
/teacher/session/<session_id>/qr/download
```

## Install

Stop Flask and ngrok. Extract the ZIP and run:

```text
INSTALL_GLOBAL_REBUILD_1_3.bat
```

The installer updates:

```text
D:\AskYourDoubtGlobal
```

It makes a full backup and preserves:

```text
database.db
ngrok.exe
static\uploads
static\qr
exports
BASE_URL
```

## Start

```powershell
cd D:\AskYourDoubtGlobal
python app.py
```

## Full Windows browser QA

```powershell
cd D:\AskYourDoubtGlobal
.\RUN_FULL_QA_1_3.bat
```

Only call Firefox/WebKit passed after this script succeeds on the Windows laptop.
