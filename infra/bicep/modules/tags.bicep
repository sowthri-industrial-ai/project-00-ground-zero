// ============================================================================
// tags.bicep · Standard tag taxonomy for the GenAI Architect Portfolio
// ============================================================================
@description('Program slug — matches naming module.')
param program string = 'genai-portfolio'

@description('Project phase — e.g. ground-zero, poc-01, production.')
param projectPhase string = 'ground-zero'

@description('Environment — dev|test|prod.')
@allowed(['dev', 'test', 'prod'])
param environment string = 'prod'

@description('Cost centre label.')
param costCenter string = 'personal-portfolio'

@description('Owner identifier.')
param owner string

@description('POC identifier.')
param pocId string

@description('IaC tool that manages the resource.')
@allowed(['bicep', 'terraform', 'manual'])
param managedBy string = 'bicep'

output tags object = {
  project: program
  'project-phase': projectPhase
  environment: environment
  'cost-center': costCenter
  owner: owner
  'poc-id': pocId
  'managed-by': managedBy
}
