// ============================================================================
// app-insights.bicep · App Insights + Log Analytics workspace-based
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('App Insights resource name')
param name string
@description('Log Analytics workspace name')
param workspaceName string
@description('Resource tags')
param tags object
@description('Retention in days')
param retentionDays int = 30

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: retentionDays
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

output connectionString string = appInsights.properties.ConnectionString
output workspaceId string = workspace.id
output resourceId string = appInsights.id
