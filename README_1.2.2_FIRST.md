# AskYourDoubt 1.2.2 — Read First

This build addresses the latest requirements:

- Home hero wording reduced to a compact commercial size.
- Teacher live-session page redesigned with a 3D kinetic visual, compact statistics, priority open-doubt queue, QR area, and Doubt Control Center.
- Student live-session page redesigned with a 3D kinetic visual, persistent tabs, silent live updates, My Question indicator, voting, and pagination.
- Live Doubts: 100 by default, optional 250 or 500, pagination only inside the live section.
- Other teacher/admin/question-bank lists use 10/20/30 pagination.
- Windows QA evidence no longer overwrites/deletes a locked screenshots folder. Every run uses a unique timestamped directory and falls back to `%TEMP%` if the project evidence path is locked.

## Install

Run:

```text
INSTALL_GLOBAL_REBUILD_1_2_2.bat
```

Target:

```text
D:\AskYourDoubtGlobal
```

The installer preserves the existing database, uploads, QR files, exports, ngrok executable, and BASE_URL.

## Start

```powershell
cd D:\AskYourDoubtGlobal
python app.py
```

## Local quality gate

```powershell
cd D:\AskYourDoubtGlobal
.\run_debug_ci_cd.bat
```

## Full browser matrix on Windows

```powershell
cd D:\AskYourDoubtGlobal
.\RUN_FULL_QA_1_2_2.bat
```

Do not claim Firefox/WebKit passed unless this finishes successfully on the laptop.
