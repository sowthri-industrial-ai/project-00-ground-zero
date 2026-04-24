// ============================================================================
// container-registry.bicep · ACR Basic
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('ACR name (5-50 alphanumeric)')
param name string
@description('Resource tags')
param tags object

resource acr 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: { name: 'Basic' }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

output loginServer string = acr.properties.loginServer
output resourceId string = acr.id
