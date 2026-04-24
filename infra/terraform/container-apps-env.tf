############################################################################
# container-apps-env.tf · Terraform mirror of container-apps-env.bicep
############################################################################
variable "cae_name"             { type = string }
variable "log_analytics_workspace_id" { type = string }

resource "azurerm_container_app_environment" "main" {
  name                       = var.cae_name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  log_analytics_workspace_id = var.log_analytics_workspace_id
  tags                       = var.tags
}

output "cae_id" { value = azurerm_container_app_environment.main.id }
