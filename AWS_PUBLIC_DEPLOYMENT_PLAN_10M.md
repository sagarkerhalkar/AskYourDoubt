# AWS Public Deployment Plan for 10,000,000 Students

## Direct answer

Do **not** deploy this current Flask + SQLite + local filesystem build directly for 10,000,000 students.

This source can run as a small public MVP after normal production hardening, but 10,000,000 students requires a cloud-native architecture change.

## Why current build is not enough for 10M students

Current source uses:
- Flask/Waitress app server
- SQLite database
- Local filesystem uploads
- Local filesystem QR/images/resources
- 1-second polling style live updates
- Docker/Caddy single-app deployment path

This is OK for a small school/coaching pilot, but not for national/global usage. SQLite and local filesystem storage become bottlenecks, and every-1-second polling from millions of users would overload app servers and database.

## Recommended AWS architecture for 10M scale

### Edge and security

- Route 53 for DNS.
- CloudFront CDN for static assets and public cached content.
- AWS WAF in front of public endpoints.
- ACM TLS certificates.
- Shield standard protections.
- Strict HTTPS only.

### Application layer

- Containerize the Flask app and run it on ECS Fargate behind an Application Load Balancer.
- Keep app containers stateless.
- Use Auto Scaling policies for ECS services.
- Keep at least two Availability Zones for high availability.

### Database layer

- Move from SQLite to Aurora PostgreSQL or RDS PostgreSQL.
- Store PII tables separately and protect them with least-privilege app access.
- Use Multi-AZ configuration.
- Add read replicas/read scaling for analytics and reporting.
- Add proper migrations with Alembic or Flask-Migrate.

### Live session layer

Current polling must be changed before 10M:
- Replace 1-second polling with WebSockets/SSE architecture.
- Use Redis/ElastiCache for session state, pub/sub, rate limiting, and fast live counters.
- Consider API Gateway WebSocket, AppSync subscriptions, or a dedicated WebSocket service on ECS.
- Keep Redis only for cache/live delivery; keep durable records in PostgreSQL.

### Storage layer

- Move uploads, QR images, teacher resources, and student resources to S3.
- Use private S3 objects with signed URLs.
- Use CloudFront signed URLs/cookies where needed.
- Teacher-facing student resource object names must remain anonymous.
- Never expose original student filenames to teacher.

### Background jobs

- Use SQS for export/ZIP jobs.
- Use ECS worker service or Lambda workers.
- Store generated exports in S3 with expiry.
- Avoid creating heavy ZIPs synchronously inside a web request.

### Observability

- CloudWatch logs and metrics.
- X-Ray/OpenTelemetry tracing.
- Alarms for latency, 5xx rate, DB connections, queue depth, Redis memory, ALB target health.
- Real-user monitoring for student mobile browsers.

### CI/CD

Existing GitHub Actions already include:
- Core pytest matrix
- Browser matrix
- Docker build
- Docker smoke test

For AWS production, extend CI/CD to:
- Build image
- Push to Amazon ECR
- Run database migration job
- Deploy to ECS through rolling or blue/green deployment
- Run smoke tests against staging
- Require approval before production

## Suggested phases

### Phase 1: Public MVP on AWS

Target: pilot use, not 10M.

- ECS Fargate + ALB
- PostgreSQL/RDS or Aurora PostgreSQL
- S3 for uploads/resources/QR
- Secrets Manager for secret key/database credentials
- CloudFront + WAF
- GitHub Actions to ECR + ECS
- Daily backup and restore test

### Phase 2: School/coaching scale

Target: thousands to lakhs of users.

- Redis/ElastiCache
- SQS export workers
- Move live polling to SSE/WebSocket
- Multi-AZ app/database/cache
- Load testing with k6/Locust
- WAF rate limits
- Admin analytics read replicas

### Phase 3: 10M student readiness

Target: large public usage.

- Multi-region architecture or at least multi-AZ high scale
- WebSocket/SSE infrastructure designed for massive fanout
- Aurora PostgreSQL tuned and partitioned by organization/session/date
- S3/CloudFront for all static and resource traffic
- Export workers separated from live app
- Strong tenant isolation and PII access controls
- Disaster recovery plan with RPO/RTO
- Security review, penetration test, privacy review, and load test evidence

## Deployment environment variables

Minimum production variables:

```env
AYD_SECRET_KEY=<long-random-secret-from-secrets-manager>
AYD_BASE_URL=https://askyourdoubt.yourdomain.com
AYD_COOKIE_SECURE=1
AYD_DEBUG=0
AYD_DATABASE=<postgresql-uri-after-db-migration>
AYD_UPLOAD_BACKEND=s3
AYD_S3_BUCKET=<bucket-name>
AYD_AWS_REGION=ap-south-1
```

The current code still expects SQLite and local paths, so database/storage migration work is required before using the PostgreSQL/S3 variables above.

## Privacy deployment rule

Teacher-facing APIs and exports must continue to exclude:
- `student_name`
- `mobile`
- `student_mobile`
- joined-student count
- original student-upload filenames

Admin-only APIs may access these fields.
