# GitHub Secrets Needed for AWS Deploy Workflow

Create these in:

`GitHub Repo -> Settings -> Secrets and variables -> Actions`

```text
AWS_REGION=ap-south-1
AWS_ACCOUNT_ID=123456789012
AWS_ECR_REPOSITORY=askyourdoubt
AWS_ECS_CLUSTER=askyourdoubt-prod
AWS_ECS_SERVICE=askyourdoubt-web
AWS_ECS_TASK_DEFINITION=deploy/aws/ecs-task-definition.example.json
AWS_ECS_CONTAINER_NAME=web
```

Recommended security: use GitHub OIDC role for AWS deploy instead of storing long-lived AWS keys.
