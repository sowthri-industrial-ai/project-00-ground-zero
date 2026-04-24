// ============================================================================
// container-apps-env.bicep · Container Apps Managed Environment
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Environment name')
param name string
@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string
@description('Resource tags')
param tags object

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

resource cae 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

output environmentId string = cae.id
output defaultDomain string = cae.properties.defaultDomain
