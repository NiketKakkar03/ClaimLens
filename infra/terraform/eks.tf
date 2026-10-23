data "aws_availability_zones" "available" { state = "available" }

resource "aws_vpc" "eks" {
  count                = var.create_eks ? 1 : 0
  cidr_block           = "10.40.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = { Name = "${local.name}-vpc" }
}

resource "aws_internet_gateway" "eks" {
  count  = var.create_eks ? 1 : 0
  vpc_id = aws_vpc.eks[0].id
}

resource "aws_subnet" "eks_public" {
  count                   = var.create_eks ? 2 : 0
  vpc_id                  = aws_vpc.eks[0].id
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = cidrsubnet(aws_vpc.eks[0].cidr_block, 8, count.index)
  map_public_ip_on_launch = true
  tags = {
    Name                                      = "${local.name}-public-${count.index + 1}"
    "kubernetes.io/role/elb"                  = "1"
    "kubernetes.io/cluster/${local.name}-eks" = "shared"
  }
}

resource "aws_route_table" "eks_public" {
  count  = var.create_eks ? 1 : 0
  vpc_id = aws_vpc.eks[0].id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.eks[0].id
  }
}

resource "aws_route_table_association" "eks_public" {
  count          = var.create_eks ? 2 : 0
  subnet_id      = aws_subnet.eks_public[count.index].id
  route_table_id = aws_route_table.eks_public[0].id
}

data "aws_iam_policy_document" "eks_cluster_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_cluster" {
  count              = var.create_eks ? 1 : 0
  name               = "${local.name}-eks-cluster"
  assume_role_policy = data.aws_iam_policy_document.eks_cluster_assume.json
}

resource "aws_iam_role_policy_attachment" "eks_cluster" {
  count      = var.create_eks ? 1 : 0
  role       = aws_iam_role.eks_cluster[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_eks_cluster" "this" {
  count    = var.create_eks ? 1 : 0
  name     = "${local.name}-eks"
  role_arn = aws_iam_role.eks_cluster[0].arn
  version  = var.eks_version
  vpc_config {
    subnet_ids              = aws_subnet.eks_public[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = var.eks_public_access_cidrs
  }
  depends_on = [aws_iam_role_policy_attachment.eks_cluster]
}

data "aws_iam_policy_document" "eks_node_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "eks_node" {
  count              = var.create_eks ? 1 : 0
  name               = "${local.name}-eks-node"
  assume_role_policy = data.aws_iam_policy_document.eks_node_assume.json
}

resource "aws_iam_role_policy_attachment" "eks_node" {
  for_each = var.create_eks ? toset([
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  ]) : toset([])
  role       = aws_iam_role.eks_node[0].name
  policy_arn = each.value
}

resource "aws_eks_node_group" "this" {
  count           = var.create_eks ? 1 : 0
  cluster_name    = aws_eks_cluster.this[0].name
  node_group_name = "${local.name}-small"
  node_role_arn   = aws_iam_role.eks_node[0].arn
  subnet_ids      = aws_subnet.eks_public[*].id
  instance_types  = ["t3.small"]
  capacity_type   = "SPOT"
  scaling_config {
    desired_size = 1
    min_size     = 1
    max_size     = 2
  }
  update_config {
    max_unavailable = 1
  }
  depends_on = [aws_iam_role_policy_attachment.eks_node]
}
