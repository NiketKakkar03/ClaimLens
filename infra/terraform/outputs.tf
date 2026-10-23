output "lakehouse_bucket" { value = aws_s3_bucket.lakehouse.id }
output "inference_repository_url" { value = aws_ecr_repository.inference.repository_url }
output "eks_enabled" { value = var.create_eks }
output "eks_cluster_name" { value = try(aws_eks_cluster.this[0].name, null) }
