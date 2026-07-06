# Security and Secrets Checklist

## Never commit these to GitHub

- Cloudflare tunnel token
- AWS access keys
- database password
- `.env`
- SQLite database file
- real student data
- real uploaded resources

## GitHub Actions secrets

GitHub repository secrets are created from:

`Repo -> Settings -> Secrets and variables -> Actions -> New repository secret`

Use repository/environment secrets only for non-public values.

Recommended secret names:

```text
AWS_REGION
AWS_ACCOUNT_ID
AWS_ECR_REPOSITORY
AWS_ECS_CLUSTER
AWS_ECS_SERVICE
AWS_ECS_TASK_DEFINITION
AWS_ECS_CONTAINER_NAME
```

Prefer GitHub OIDC to AWS instead of long-lived AWS access keys.

## Production privacy rule

Teacher must not see student name, mobile, joined count, or student list. Add tests for every future change.
