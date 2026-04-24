############################################################################
# main.tf · Providers and shared variables
############################################################################
terraform {
  required_version = ">= 1.9.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.10"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location"            { type = string; default = "swedencentral" }
variable "resource_group_name" { type = string }
variable "tags"                { type = map(string) }
