variable "name" {
  description = "Name of the deployment"
  type        = string
  default     = "mcp-gateway"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "certificate_arn" {
  description = "ARN of ACM certificate for HTTPS (optional, creates HTTP-only if not provided)"
  type        = string
  default     = ""
}

variable "enable_monitoring" {
  description = "Whether to enable CloudWatch monitoring and alarms"
  type        = bool
  default     = true
}

variable "alarm_email" {
  description = "Email address for CloudWatch alarm notifications"
  type        = string
  default     = ""
}

variable "keycloak_client_secret" {
  description = "Keycloak client secret for web application OAuth2. Get this from Keycloak Admin Console > Clients > mcp-gateway-web > Credentials > Secret"
  type        = string
  default     = "change-me-to-keycloak-web-client-secret"
  sensitive   = true
}

variable "keycloak_m2m_client_secret" {
  description = "Keycloak machine-to-machine client secret for Admin API. Get this from Keycloak Admin Console > Clients > mcp-gateway-m2m > Credentials > Secret"
  type        = string
  default     = "change-me-to-keycloak-m2m-client-secret"
  sensitive   = true
}