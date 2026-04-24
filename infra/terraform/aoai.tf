############################################################################
# aoai.tf · Terraform mirror of aoai.bicep
############################################################################
variable "aoai_name" { type = string }

resource "azurerm_cognitive_account" "aoai" {
  name                  = var.aoai_name
  location              = var.location
  resource_group_name   = var.resource_group_name
  kind                  = "OpenAI"
  sku_name              = "S0"
  custom_subdomain_name = var.aoai_name
  local_auth_enabled    = false
  tags                  = var.tags

  identity { type = "SystemAssigned" }
}

resource "azurerm_cognitive_deployment" "gpt4o_mini" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.aoai.id
  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }
  sku {
    name     = "GlobalStandard"
    capacity = 50
  }
}

resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.aoai.id
  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }
  sku {
    name     = "GlobalStandard"
    capacity = 10
  }
  depends_on = [ azurerm_cognitive_deployment.gpt4o_mini ]
}

resource "azurerm_cognitive_deployment" "embed" {
  name                 = "text-embedding-3-small"
  cognitive_account_id = azurerm_cognitive_account.aoai.id
  model {
    format  = "OpenAI"
    name    = "text-embedding-3-small"
    version = "1"
  }
  sku {
    name     = "Standard"
    capacity = 50
  }
  depends_on = [ azurerm_cognitive_deployment.gpt4o ]
}

output "aoai_endpoint" { value = azurerm_cognitive_account.aoai.endpoint }
