// ============================================================================
// aoai.bicep · Azure OpenAI + 3 model deployments
// Entra-only auth · no API keys · architect signal
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('AOAI resource name')
param name string
@description('Resource tags')
param tags object

resource aoai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: name
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: name
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
}

resource gpt4oMini 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'gpt-4o-mini'
  sku: { name: 'GlobalStandard', capacity: 50 }
  properties: {
    model: { format: 'OpenAI', name: 'gpt-4o-mini', version: '2024-07-18' }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

resource gpt4o 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'gpt-4o'
  sku: { name: 'GlobalStandard', capacity: 10 }
  properties: {
    model: { format: 'OpenAI', name: 'gpt-4o', version: '2024-11-20' }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
  dependsOn: [ gpt4oMini ]
}

resource embed 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'text-embedding-3-small'
  sku: { name: 'Standard', capacity: 50 }
  properties: {
    model: { format: 'OpenAI', name: 'text-embedding-3-small', version: '1' }
  }
  dependsOn: [ gpt4o ]
}

output endpoint string = aoai.properties.endpoint
output resourceId string = aoai.id
output principalId string = aoai.identity.principalId
