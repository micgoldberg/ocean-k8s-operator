provider "spotinst" {
  token = var.spotinst_token
  account = var.spotinst_account
}

terraform {
  required_providers {
    spotinst = {
      source = "spotinst/spotinst"
    }
  }
}

module "ocean-aws-k8s-vng" {
  source = "spotinst/ocean-aws-k8s-vng/spotinst"
  version = "0.13.0"

  name = var.name
  ocean_id = var.ocean_id

  spot_percentage = var.spot_percentage
}