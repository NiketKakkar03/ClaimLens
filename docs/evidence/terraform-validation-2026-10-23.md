# Terraform AWS foundation evidence — 2026-10-23

## Scope

The MVP infrastructure configuration defines:

- private, encrypted, versioned S3 lakehouse storage with public access blocked;
- an encrypted ECR repository with immutable tags, scan-on-push, and image retention;
- least-purpose EKS cluster and node IAM roles;
- optional two-subnet VPC, EKS control plane, and one-to-two Spot worker nodes;
- an optional forecasted AWS Budget notification.

EKS defaults to disabled. The configuration therefore makes the expensive part an explicit choice rather than an accidental consequence of learning Terraform. The public EKS endpoint defaults to a non-routable local `/32` placeholder, which must be replaced by the operator's current public IP before an approved exercise.

## Verification

Terraform 1.10 ran in a local Docker container. `terraform init -backend=false`, recursive formatting, and `terraform validate` completed successfully. Provider selections are committed in `.terraform.lock.hcl`; generated provider binaries and state files are ignored.

No `terraform apply` was run, no AWS API mutation occurred, and no cloud cost was created. A real plan still requires the user's AWS identity and account-specific review. Applying EKS remains outside the local MVP because even a short-lived cluster can incur charges.

## Safety boundary

An AWS Budget only notifies; it does not stop resources or cap spending. Before any future apply, verify credits, current EKS version availability, region, public-IP allowlist, expected hourly cost, and same-day destroy procedure. Use `terraform plan` for review and never commit credentials or `terraform.tfvars`.
