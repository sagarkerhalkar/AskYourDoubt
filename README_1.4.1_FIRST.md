# Read First — AskYourDoubt 1.4.1

This version fixes the automatic teacher/student logout bug caused by one browser cookie being cleared by another portal role.

## Install

1. Stop Flask/Waitress and ngrok/Cloudflare Tunnel.
2. Extract the ZIP.
3. Run `INSTALL_GLOBAL_REBUILD_1_4_1.bat`.
4. Start the application.
5. Test teacher and student in two tabs of the same browser.
6. Run `RUN_FULL_QA_1_4_1.bat`.

The installer backs up `D:\AskYourDoubtGlobal` and preserves the database, uploads, resources, QR files, exports, logo, ngrok executable, and BASE_URL.
