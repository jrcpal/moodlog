variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefix for resource names and tags"
  type        = string
  default     = "moodlog"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "my_ip" {
  description = "Your public IP in CIDR notation (e.g. 71.191.42.99/32)"
  type        = string
}

variable "db_name" {
  description = "Name of the database inside RDS"
  type        = string
  default     = "moodlog"
}

variable "db_username" {
  description = "Master username for RDS"
  type        = string
  default     = "moodlog_admin"
}

variable "db_password" {
  description = "Master password for RDS. Set in terraform.tfvars."
  type        = string
  sensitive   = true
}