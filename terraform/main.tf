data "aws_availability_zones" "available" {}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "6.5.0"

  name                 = "temporal-infra-workflow"
  cidr                 = "10.0.0.0/16"
  azs                  = slice(data.aws_availability_zones.available.names, 0, 3)
  public_subnets       = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]
  enable_dns_hostnames = true
  enable_dns_support   = true
}


resource "aws_security_group" "allow_ssh" {
  name        = "temporal-infra-workflow-allow-ssh"
  description = "Allow SSH from anywhere"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "demo_rds"
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "tls_private_key" "generated" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated" {
  key_name   = "temporal-infra-workflow-key"
  public_key = tls_private_key.generated.public_key_openssh
}

resource "local_file" "pem_file" {
  content         = tls_private_key.generated.private_key_pem
  filename        = "${path.module}/temporal-infra-workflow-key.pem"
  file_permission = "0600"
}

resource "aws_instance" "basic" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.micro"
  vpc_security_group_ids      = [aws_security_group.allow_ssh.id]
  subnet_id                   = element(module.vpc.public_subnets, 0)
  key_name                    = aws_key_pair.generated.key_name
  associate_public_ip_address = true

  tags = {
    Environment = "dev"
    Owner       = "polina.jastr@gmail.com"
    Name        = "temporal-infra-workflow"
  }
}