// ============================================================================
// naming.bicep · Reusable naming convention module
// ----------------------------------------------------------------------------
// Produced by:  Brief A · Platform & Identity · Wave 1
// Consumed by:  Briefs B, C, D, E (and all downstream portfolio projects)
// Convention:   <resourceType>-<program>-<seq>[-<uniqueSuffix>]
//               e.g.  kv-genai-portfolio-01-abc123
// ============================================================================

@description('Program slug — lowercase, hyphen-separated, used as naming middle.')
param program string = 'genai-portfolio'

@description('Resource type short code. Standard codes: aoai|srch|cosmos|kv|mi|ca|cae|log|st|acr|appi.')
param resourceType string

@description('Sequence number as a two-digit string (01, 02, ...).')
param seq string = '01'

@description('Optional suffix for globally-unique resources (e.g. Key Vault, Storage). Leave empty when not required.')
param uniqueSuffix string = ''

output resourceName string = empty(uniqueSuffix)
  ? '${resourceType}-${program}-${seq}'
  : '${resourceType}-${program}-${seq}-${uniqueSuffix}'
