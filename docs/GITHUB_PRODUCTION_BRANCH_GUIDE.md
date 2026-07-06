# GitHub Production Branch Guide

Repository: `https://github.com/sagarkerhalkar/AskYourDoubt`

## Goal

Create/update a clean `production` branch with the current production-ready source, AWS deployment files, CI/CD workflows, and documentation.

## Branches

```text
main        = development branch
production  = deployable branch for customer/demo/AWS
```

## Files that must not be committed

```text
.env
database.db
ngrok.exe
*.pyc
__pycache__/
.pytest_cache/
.venv/
uploads/
qr/
backups/
```

## Local update commands

Run from PowerShell after extracting this clean package:

```powershell
git clone https://github.com/sagarkerhalkar/AskYourDoubt.git
cd AskYourDoubt
git checkout main
git pull origin main
git checkout -B production

# Copy all files from the clean production package into this repo folder.
# Then check status:
git status

git add .
git commit -m "Production release v1.6.10 with AWS deployment structure"
git push -u origin production --force-with-lease
```

Use `--force-with-lease` only when you intentionally want local `production` to replace the remote `production` branch safely.

## After push

1. Open GitHub repository.
2. Change branch dropdown to `production`.
3. Open Actions tab.
4. Confirm CI tests start.
5. Fix any failed test before using for AWS production.
