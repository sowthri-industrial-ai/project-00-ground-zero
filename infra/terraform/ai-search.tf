############################################################################
# ai-search.tf · Terraform mirror of ai-search.bicep
############################################################################
variable "search_name" { type = string }

resource "azurerm_search_service" "main" {
  name                = var.search_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "free"
  replica_count       = 1
  partition_count     = 1
  tags                = var.tags
}

output "search_endpoint" { value = "https://${azurerm_search_service.main.name}.search.windows.net" }
