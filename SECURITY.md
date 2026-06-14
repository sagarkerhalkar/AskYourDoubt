# Security

Do not publish credentials, database files, uploads, exports, QR files, backups, or `.env` files.

Before public deployment:

- change the default administrator password;
- set a strong `AYD_SECRET_KEY`;
- use HTTPS;
- keep role and ownership authorization checks;
- maintain verified backups;
- define privacy and retention rules for student data;
- keep dependencies and container images patched;
- review file-upload validation and access controls.
