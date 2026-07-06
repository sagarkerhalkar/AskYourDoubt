# AskYourDoubt Production App Structure

This branch is the clean production branch for the AskYourDoubt live classroom doubt platform.

## Important privacy rule

Teacher views and teacher APIs must never expose:

- student name
- student mobile number
- joined-student count
- joined-student list
- original student attachment filename if it can contain personal data

Student private data remains admin-only.

## Main runtime files

```text
app.py                 Flask app entry point
config.py              Environment/config loading
db.py                  SQLite/PostgreSQL-ready database helper and migrations
auth.py                Login/session helper logic
utils.py               Shared helpers
routes/                Route modules by role
  admin.py             Admin dashboard, student records, teacher/session management
  api.py               Live APIs and async endpoints
  public.py            Home/login/public routes
  student.py           Student join, ask, live, answered, resources
  teacher.py           Teacher live session, question bank, resources, exports
static/                CSS, JS, images, UI assets
templates/             Jinja HTML templates
tests/                 Pytest functional tests
browser_tests/         Playwright browser/device tests
.github/workflows/     CI/CD workflows
Dockerfile             Production container image
compose.yaml           Local Docker run
compose.production.yaml Production-style compose reference
deploy/aws/            AWS ECS/Fargate deployment reference
```

## Branch policy

- `main`: development / active fixes
- `production`: clean deployable branch
- `feature/*`: experimental changes

## Current production target

- Version: 1.6.10
- Session duration input: hours-style display, 0 to 24 hours
- Examples: `0` manual, `.30` 30 minutes, `1.30` 90 minutes, `24` maximum
- Responsive targets: mobile, tablet, laptop, desktop, Safari/WebKit, Chrome, Edge, Firefox
