// ============================================================================
// managed-identity.bicep · User-assigned managed identity
// ============================================================================
@description('Azure region.')
param location string = 'swedencentral'

@description('Managed Identity name.')
param name string

@description('Resource tags.')
param tags object

resource mi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

output identityId string = mi.id
output identityName string = mi.name
output principalId string = mi.properties.principalId
output clientId string = mi.properties.clientId
