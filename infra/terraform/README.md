# AWS Terraform foundation

This configuration defines encrypted private S3 storage, an immutable/scanned ECR repository, scoped EKS service roles, optional networking and a small Spot-backed EKS node group, plus an optional AWS Budget notification.

`create_eks` defaults to `false` because an EKS control plane and nodes cost money even when idle. Validation and planning do not create resources. An AWS Budget is an alert, not a hard spending cap.

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check
terraform validate
terraform plan
```

Do not run `terraform apply` until credits, region, plan contents, teardown commands, expected hourly cost, a currently supported EKS version, and your `/32` public IP allowlist have been reviewed. If a short-lived EKS exercise is approved later, set `create_eks = true`, apply, capture evidence, and run `terraform destroy` the same day. Leaving `eks_version = null` asks AWS for its current default and avoids silently pinning an obsolete control-plane release.
