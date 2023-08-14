variable "region" {
    description = "Region for aws"
    default = "us-east-1"
}

variable "profile" {
    description = "AWS profile name"
    default = "" 
}

variable "s3_bucket" {
    description = "s3 bucket name"
    default = "" 
}

variable "rds_database" {
    description = "RDS database name"
    default = "" 
}

variable "rds_username" {
    description = "RDS username"
    default = ""
}

variable "rds_password" {
    description = "RDS password"
    default = ""
}

variable "rds_instance" {
    description = "RDS instance"
    default = ""
}

variable "ec2_instance" {
    description = "EC2 instance"
    default = ""
}



