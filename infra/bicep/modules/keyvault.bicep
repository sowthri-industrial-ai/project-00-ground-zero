// ============================================================================
// keyvault.bicep · Standard Key Vault for portfolio projects
// ============================================================================
@description('Azure region. Default: swedencentral.')
param location string = 'swedencentral'

@description('Key Vault name. Globally unique; 3-24 chars.')
@minLength(3)
@maxLength(24)
param name string

@description('Resource tags.')
param tags object

@description('Entra tenant ID.')
param tenantId string = subscription().tenantId

@description('Use RBAC for data-plane authorisation.')
param enableRbac bool = true

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: enableRbac
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: false
    publicNetworkAccess: 'Enabled'
  }
}

output keyVaultId string = kv.id
output keyVaultName string = kv.name
output keyVaultUri string = kv.properties.vaultUri
