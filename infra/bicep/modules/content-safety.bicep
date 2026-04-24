// ============================================================================
// content-safety.bicep · Content Safety F0 (free tier)
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Content Safety resource name')
param name string
@description('Resource tags')
param tags object

resource cs 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: 'ContentSafety'
  sku: { name: 'F0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}

output endpoint string = cs.properties.endpoint
output resourceId string = cs.id
