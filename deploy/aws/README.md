# AWS Deployment Reference

This folder contains reference files for deploying AskYourDoubt on AWS ECS Fargate.

## Recommended AWS architecture

```text
Customer subdomain
  -> HTTPS / ACM certificate
  -> Application Load Balancer
  -> ECS Fargate service running AskYourDoubt containers
  -> RDS PostgreSQL database
  -> S3 private buckets for uploads/resources/exports
  -> CloudWatch logs and metrics
```

## First paid pilot sizing

```text
ECS tasks: 4
Each task: 2 vCPU / 4 GB RAM
RDS: db.t4g.medium or db.t4g.large
S3: private encrypted buckets
ALB: HTTPS listener with /healthz check
```

Scale up after load testing.
