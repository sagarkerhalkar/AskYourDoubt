# AWS Implementation - Step by Step for AskYourDoubt

This document is written for a beginner implementation. It explains what to click and what to create.

## Stage 1: Free demo

Use your laptop + Cloudflare Tunnel for a 5-10 teacher / 50 student demo.

1. Run the app locally on port `9000`.
2. In Cloudflare Zero Trust, add a public hostname such as `demo.askyourdoubt.sagarkerhalkar.com`.
3. Route it to `http://localhost:9000`.
4. Restart the app with `AYD_BASE_URL=https://demo.askyourdoubt.sagarkerhalkar.com`.

This is only for demo. Do not use this for 10,000+ live students.

## Stage 2: AWS paid pilot

Use this when a customer expects 10,000 to 60,000 live students.

### AWS services to create

| Service | Simple meaning | Start setting |
|---|---|---|
| ECR | Stores Docker image | One repository: `askyourdoubt` |
| ECS Fargate | Runs app containers | 4 tasks to start |
| Application Load Balancer | Public HTTPS front door | 80 -> 443 redirect, health `/healthz` |
| RDS PostgreSQL | Production database | db.t4g.medium or higher |
| S3 | Uploads/resources/videos/exports | Private buckets, encryption on |
| ACM | Free SSL certificate | DNS validation |
| CloudWatch | Logs/errors/delay monitoring | log group per service |
| Secrets Manager | Stores passwords safely | DB URL, secret key |

### Click-by-click summary

1. Login to AWS Console.
2. Select region: `Asia Pacific (Mumbai) ap-south-1`.
3. Enable MFA on root account.
4. Create AWS Budget alerts: ₹2,000, ₹5,000, ₹10,000, ₹25,000.
5. Create ECR repository: `askyourdoubt`.
6. Build Docker image locally.
7. Push Docker image to ECR.
8. Create RDS PostgreSQL database in private subnet.
9. Create S3 private buckets:
   - `askyourdoubt-prod-uploads`
   - `askyourdoubt-prod-resources`
   - `askyourdoubt-prod-exports`
10. Create ECS Fargate cluster: `askyourdoubt-prod`.
11. Create ECS task definition using the ECR image.
12. Create ECS service with Application Load Balancer.
13. Request SSL certificate in ACM for customer subdomain.
14. Ask customer IT to point CNAME to ALB DNS name.
15. Open CloudWatch and watch logs + latency.
16. Run smoke test: admin login, teacher session, student join, doubt submit.

## Starting environment variables

```text
AYD_ENV=production
AYD_PORT=9000
AYD_BASE_URL=https://CUSTOMER_SUBDOMAIN
AYD_SECRET_KEY=USE_SECRETS_MANAGER_NOT_GITHUB
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/askyourdoubt
S3_BUCKET_UPLOADS=askyourdoubt-prod-uploads
S3_BUCKET_RESOURCES=askyourdoubt-prod-resources
S3_BUCKET_EXPORTS=askyourdoubt-prod-exports
```

## Cost expectation

| Stage | Approx monthly cost |
|---|---:|
| Free demo | ₹0 |
| Small AWS pilot | ₹8,000 - ₹25,000 |
| 10k-20k live students | ₹50,000 - ₹1,50,000 |
| 40k-60k live students | ₹1,50,000 - ₹5,00,000+ |

Final cost depends on live users, file/video usage, polling frequency, database size, and bandwidth.
