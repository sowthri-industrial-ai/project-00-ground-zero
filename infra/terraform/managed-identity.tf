############################################################################
# managed-identity.tf · Terraform mirror of managed-identity.bicep
############################################################################
variable "mi_name"                { type = string }
variable "mi_location"            { type = string; default = "swedencentral" }
variable "mi_resource_group_name" { type = string }
variable "mi_tags"                { type = map(string) }

resource "azurerm_user_assigned_identity" "main" {
  name                = var.mi_name
  location            = var.mi_location
  resource_group_name = var.mi_resource_group_name
  tags                = var.mi_tags
}

output "identity_id"   { value = azurerm_user_assigned_identity.main.id }
output "identity_name" { value = azurerm_user_assigned_identity.main.name }
output "principal_id"  { value = azurerm_user_assigned_identity.main.principal_id }
output "client_id"     { value = azurerm_user_assigned_identity.main.client_id }
