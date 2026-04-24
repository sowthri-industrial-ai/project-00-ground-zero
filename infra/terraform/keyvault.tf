############################################################################
# keyvault.tf · Terraform mirror of keyvault.bicep
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
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

variable "location"            { type = string; default = "swedencentral" }
variable "resource_group_name" { type = string }
variable "name" {
  type = string
  validation {
    condition     = length(var.name) >= 3 && length(var.name) <= 24
    error_message = "Key Vault name must be 3-24 characters."
  }
}
variable "tags"      { type = map(string) }
variable "tenant_id" { type = string }

resource "azurerm_key_vault" "main" {
  name                          = var.name
  location                      = var.location
  resource_group_name           = var.resource_group_name
  tenant_id                     = var.tenant_id
  sku_name                      = "standard"
  enable_rbac_authorization     = true
  soft_delete_retention_days    = 7
  purge_protection_enabled      = false
  public_network_access_enabled = true
  tags                          = var.tags
}

output "key_vault_id"   { value = azurerm_key_vault.main.id }
output "key_vault_name" { value = azurerm_key_vault.main.name }
output "key_vault_uri"  { value = azurerm_key_vault.main.vault_uri }
