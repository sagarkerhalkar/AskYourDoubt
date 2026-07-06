# AskYourDoubt 1.5.2 Handoff

Use this folder as the current source. Do not overwrite it with templates, CSS, JavaScript, routes or database files from an older build.

## Start on Windows

```powershell
cd D:\AskYourDoubtGlobal
.\INSTALL_1_5_2.bat
.\start_waitress.bat
```

Open `http://127.0.0.1:9000`.

## Required validation

```powershell
.\RUN_FULL_QA_1_5_2.bat
```

Read these files before reporting success:

- `README.md`
- `TEST_REPORT_1.5.2.md`
- `REQUIREMENTS_TRACEABILITY_1.5.2.md`
- `CHANGELOG_1.5.2.md`

## Important 1.5.2 behavior

- Total Questions and Total CSV mean Open + Completed.
- Skipped questions remain separate and hidden from students.
- Teacher Completed and Skipped lists have independent pagination.
- Student Answered has independent pagination.
- QR/link can be maximized or opened in the dedicated Full Page view.
- The final branded palette is navy, sky-blue, white and cool grey.
