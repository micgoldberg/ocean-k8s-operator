variable "spotinst_account" {
  description = "Your Spotinst account ID"
  type        = string
}

variable "spotinst_token" {
  description = "Your Spotinst token"
  type        = string
}

variable "name" {
  description = "Name for nodegroup (VNG)"
  type        = string
}

variable "ocean_id" {
  description = "The Ocena cluster ID"
  type        = string
}

variable "spot_percentage" {
  description = "Percentage of VNG that will run on EC2 Spot instances and remaining will run on-demand"
  type        = number
}