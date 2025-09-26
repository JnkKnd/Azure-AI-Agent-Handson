// ==== パラメータ ====
param location string
param pgServerName string
param pgDbName string
param pgAdminUser string
@secure()
param pgAdminPassword string
param cosmosAccountName string
param cosmosDbName string
param cosmosContainerName string
param cosmosPartitionKey string
param cosmosDbThroughput int
param aiFoundryName string
param aiProjectName string
param aiModelDeploymentName string = 'gpt-4.1-mini'

// Azure AI Search
param aiSearchName string
param blobStorageName string
param logicAppName string

// Azure OpenAI
param azureOpenAIName string
param embeddingModelName string = 'text-embedding-ada-002'

// ===== PostgreSQL Flexible Server =====
resource pgServer 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: pgServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '15'
    administratorLogin: pgAdminUser
    administratorLoginPassword: pgAdminPassword
    storage: { storageSizeGB: 32 }
    highAvailability: { mode: 'Disabled' }
    network: { publicNetworkAccess: 'Enabled' }
  }
}

// ===== PostgreSQL DB作成 =====
resource pgDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: pgServer
  name: pgDbName
  properties: {}
}

// ===== FWルール =====
resource pgFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: pgServer
  name: 'allowall'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}

// ===== Cosmos DB アカウント =====
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2025-04-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    capabilities: []
    publicNetworkAccess: 'Enabled'
  }
}

// ===== Cosmos DB データベース =====
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2025-04-15' = {
  parent: cosmosAccount
  name: cosmosDbName
  properties: {
    resource: {
      id: cosmosDbName
    }
  }
}

// ===== Cosmos DB コンテナ =====
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2025-04-15' = {
  parent: cosmosDb
  name: cosmosContainerName
  properties: {
    resource: {
      id: cosmosContainerName
      partitionKey: {
        paths: [cosmosPartitionKey]
        kind: 'Hash'
      }
    }
    options: {
      throughput: cosmosDbThroughput
    }
  }
}

// ==== AI Foundry Account ====
resource aiFoundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiFoundryName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  properties: {
    allowProjectManagement: true
    customSubDomainName: toLower(aiFoundryName)
    disableLocalAuth: false // ローカル認証を無効化（本番環境では非推奨）※ https://learn.microsoft.com/en-us/azure/ai-services/disable-local-auth
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
  }
}

// ==== AI Foundry Project ====
resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  name: aiProjectName
  parent: aiFoundry
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

// ==== AI Foundry Model Deployment ====
resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiFoundry
  name: aiModelDeploymentName
  sku : {
    capacity: 10
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: aiModelDeploymentName
      format: 'OpenAI'
    }
  }
}

// ==== Azure OpenAI Resource ====
resource azureOpenAI 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: azureOpenAIName
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'OpenAI'
  properties: {
    customSubDomainName: toLower(azureOpenAIName)
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

// ==== Azure OpenAI Embedding Model Deployment ====
resource embeddingModelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: azureOpenAI
  name: embeddingModelName
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: '2'
    }
  }
}

// ===== Azure AI Search =====
resource aiSearch 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: aiSearchName
  location: location
  sku: {
    name: 'basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    semanticSearch: 'free'
  }
}

// ===== Blob Storage =====
resource blobStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: blobStorageName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
    minimumTlsVersion: 'TLS1_2'
  }
}

// ===== Logic Apps (Multi-tenant consumption) =====
resource logicApp 'Microsoft.Logic/workflows@2019-05-01' = {
  name: logicAppName
  location: location
  properties: {
    state: 'Enabled'
    definition: {
      '$schema': 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
      contentVersion: '1.0.0.0'
      parameters: {}
      triggers: {}
      actions: {}
      outputs: {}
    }
  }
}

// ===== 出力 =====
output pgServerFqdn string = pgServer.properties.fullyQualifiedDomainName
output cosmosAccountEndpoint string = cosmosAccount.properties.documentEndpoint
output cosmosAccountName string = cosmosAccountName
output cosmosDbName string = cosmosDbName
output cosmosContainerName string = cosmosContainerName
output aiFoundryName string = aiFoundry.name
output aiProjectName string = aiProject.name
output aiModelDeploymentName string = modelDeployment.name
output azureOpenAIName string = azureOpenAI.name
output azureOpenAIEndpoint string = azureOpenAI.properties.endpoint
output embeddingModelName string = embeddingModelDeployment.name
output aiSearchName string = aiSearch.name
output aiSearchEndpoint string = 'https://${aiSearch.name}.search.windows.net'
output blobStorageName string = blobStorage.name
output blobStorageEndpoint string = blobStorage.properties.primaryEndpoints.blob
output logicAppName string = logicApp.name
