// ============================================================================
// container-app.bicep · Generic reusable Container App
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Container App name')
param name string
@description('Container Apps Environment ID')
param environmentId string
@description('Managed Identity resource ID (user-assigned)')
param managedIdentityId string
@description('Container image reference')
param image string
@description('Target port')
param targetPort int = 8080
@description('Environment variables')
param envVars array = []
@description('Resource tags')
param tags object
@description('Min replicas')
param minReplicas int = 0
@description('Max replicas')
param maxReplicas int = 3

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${managedIdentityId}': {} }
  }
  properties: {
    environmentId: environmentId
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: name
          image: image
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: envVars
          probes: [
            { type: 'Liveness', httpGet: { path: '/health', port: targetPort }, initialDelaySeconds: 10 }
            { type: 'Readiness', httpGet: { path: '/ready', port: targetPort }, initialDelaySeconds: 5 }
          ]
        }
      ]
      scale: { minReplicas: minReplicas, maxReplicas: maxReplicas }
    }
  }
}

output fqdn string = app.properties.configuration.ingress.fqdn
output resourceId string = app.id
