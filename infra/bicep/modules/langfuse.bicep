// ============================================================================
// langfuse.bicep · Self-hosted Langfuse v3 on Container Apps
// Composite module · requires Postgres Flexible Server
// ============================================================================
@description('Azure region')
param location string = 'swedencentral'
@description('Langfuse Container App name')
param name string
@description('Container Apps Environment ID')
param environmentId string
@description('Managed Identity resource ID')
param managedIdentityId string
@description('Postgres server name')
param postgresServerName string
@description('Postgres admin password (from Key Vault)')
@secure()
param postgresPassword string
@description('Resource tags')
param tags object

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-12-01-preview' = {
  name: postgresServerName
  location: location
  tags: tags
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    administratorLogin: 'langfuse'
    administratorLoginPassword: postgresPassword
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7 }
    network: { publicNetworkAccess: 'Enabled' }
    highAvailability: { mode: 'Disabled' }
  }
}

resource langfuseDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-12-01-preview' = {
  parent: postgres
  name: 'langfuse'
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}

resource langfuse 'Microsoft.App/containerApps@2024-03-01' = {
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
      ingress: { external: true, targetPort: 3000, transport: 'auto' }
    }
    template: {
      containers: [
        {
          name: 'langfuse'
          image: 'langfuse/langfuse:3'
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'DATABASE_URL', value: 'postgresql://langfuse:${postgresPassword}@${postgres.properties.fullyQualifiedDomainName}:5432/langfuse' }
            { name: 'NEXTAUTH_URL', value: 'https://${name}.${environmentId}' }
            { name: 'NEXTAUTH_SECRET', value: 'change-me-in-wave-4' }
            { name: 'SALT', value: 'change-me-in-wave-4' }
          ]
          probes: [
            { type: 'Liveness', httpGet: { path: '/api/public/health', port: 3000 }, initialDelaySeconds: 30 }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 2 }
    }
  }
  dependsOn: [ langfuseDb ]
}

output fqdn string = langfuse.properties.configuration.ingress.fqdn
output postgresFqdn string = postgres.properties.fullyQualifiedDomainName
