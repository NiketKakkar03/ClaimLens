variable "aws_region" {
  description = "AWS region used for the disposable learning environment."
  type        = string
  default     = "ca-central-1"
}

variable "environment" {
  description = "Short isolated environment name."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging"], var.environment)
    error_message = "Only dev or staging are supported by this learning stack."
  }
}

variable "cost_owner" {
  description = "Tag used to identify who must tear down the resources."
  type        = string
  default     = "local-learner"
}

variable "create_eks" {
  description = "Explicit cost gate. EKS and worker nodes are absent unless deliberately enabled."
  type        = bool
  default     = false
}

variable "eks_version" {
  description = "Optional supported EKS version. Null asks AWS to use its current default."
  type        = string
  default     = null
}

variable "eks_public_access_cidrs" {
  description = "Operator CIDRs allowed to reach the EKS public API endpoint. Replace before enabling EKS."
  type        = list(string)
  default     = ["127.0.0.1/32"]
}

variable "monthly_budget_usd" {
  description = "Notification threshold; a budget does not cap or stop AWS charges."
  type        = number
  default     = 10
}

variable "budget_email" {
  description = "Optional email for AWS Budget notifications. Empty disables the budget resource."
  type        = string
  default     = ""
}
