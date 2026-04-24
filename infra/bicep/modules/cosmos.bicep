// ============================================================================
// cosmos.bicep · Cosmos DB serverless · Entra-only auth
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Cosmos account name')
param name string
@description('Resource tags')
param tags object
@description('Database name')
param databaseName string = 'hello-ai'

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' = {
  name: name
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [ { locationName: location, failoverPriority: 0 } ]
    capabilities: [ { name: 'EnableServerless' } ]
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource db 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-11-15' = {
  parent: cosmos
  name: databaseName
  properties: { resource: { id: databaseName } }
}

resource conversations 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-11-15' = {
  parent: db
  name: 'conversations'
  properties: {
    resource: {
      id: 'conversations'
      partitionKey: { paths: [ '/session_id' ], kind: 'Hash' }
    }
  }
}

output endpoint string = cosmos.properties.documentEndpoint
output resourceId string = cosmos.id
