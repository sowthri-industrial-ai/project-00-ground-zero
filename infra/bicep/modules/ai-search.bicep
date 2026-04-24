// ============================================================================
// ai-search.bicep · AI Search Free tier
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Search service name')
param name string
@description('Resource tags')
param tags object

resource search 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: { name: 'free' }
  properties: {
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    authOptions: { apiKeyOnly: {} }
  }
}

output endpoint string = 'https://${search.name}.search.windows.net'
output resourceId string = search.id
