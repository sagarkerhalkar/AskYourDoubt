# AskYourDoubt Production Deployment Profile

## Demo profile URL

Use `https://demo.askyourdoubt.sagarkerhalkar.com` for free demo through Cloudflare Tunnel.

## Customer production URL

Use the customer-provided subdomain, for example:

```text
doubt.customer-domain.com
```

## Production rule

Free demo is okay for 50 students. Paid AWS deployment is required for 10,000-60,000 live students.

## Health check

```text
/healthz
```

## Test commands

```powershell
python -m compileall -q app.py db.py auth.py utils.py routes
python -m pytest -q tests
python run_device_matrix.py
```
