#https://www.linkedin.com/pulse/how-automatically-build-airflow-client-aws-ec2-backed-jo%C3%A3o-luis-lins/

provider "aws" {
    region = var.region
    profile = var.profile
}


module "vpc" {
  source               = "terraform-aws-modules/vpc/aws"
  name                 = "tia-vpc"
  cidr                 = "10.10.0.0/16"
  azs                  = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets      = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  public_subnets       = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
  enable_dns_hostnames = true
}

resource "aws_s3_bucket" "tia_bucket" {
    bucket = var.s3_bucket
    force_destroy = true
}


resource "aws_db_instance" "tia-database" {

  identifier             = "tia-database" # change this a/c to need
  allocated_storage      = 10
  engine                 = "postgres"
  engine_version         = "12"
  instance_class         = var.rds_instance
  db_name                = var.rds_database
  username               = var.rds_username
  password               = var.rds_password
  multi_az               = false
  db_subnet_group_name   = aws_db_subnet_group.tia_subnetgroup.name
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.allow_tia_database.id]
  port                   = "5432"
}

resource "aws_db_subnet_group" "tia_subnetgroup" {

  name        = "tia-database-subnetgroup"
  description = "tia database subnet group"
  subnet_ids  = [module.vpc.public_subnets[0], module.vpc.public_subnets[1]]
}

resource "aws_security_group" "allow_tia_database" {
  name        = "allow_tia_database"
  description = "Controlling traffic to and from tia rds instance."
  vpc_id      = module.vpc.vpc_id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "allow_tia_database" {
  security_group_id = aws_security_group.allow_tia_database.id
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks = [
  "${aws_instance.tia_instance.private_ip}/32"]
}

#keys for ec2
resource "tls_private_key" "prik" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "tia_key"
  public_key = tls_private_key.prik.public_key_openssh
}

resource "aws_security_group" "tia_security_group" {
  name        = "tia_security"
  description = "tia security group."
  vpc_id      = module.vpc.vpc_id
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] 
  }
}


resource "aws_instance" "tia_instance" {

  associate_public_ip_address = true
  ami                         = "ami-053b0d53c279acc90" # you can change this ami
  key_name                    = aws_key_pair.generated_key.key_name
  instance_type               = var.ec2_instance
  subnet_id                   = module.vpc.public_subnets[0]
  vpc_security_group_ids      = [aws_security_group.tia_security_group.id]

  root_block_device {
    delete_on_termination = true
    volume_size           = 10
  }

  tags = {
    Name = "tia"
  }

  depends_on = [aws_db_instance.tia-database]
}

output "rds_endpoint" {
  value = aws_db_instance.tia-database.endpoint
}

output "private_key" {
  value = tls_private_key.prik.private_key_pem
  sensitive = true
}

output "ec2_public_ip" {
  value = aws_instance.tia_instance.public_ip
}

