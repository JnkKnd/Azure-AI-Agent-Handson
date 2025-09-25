#!/bin/bash

# set -x # スクリプト内で実行されるコマンドを一行ずつ表示（デバッグ用）
set -e # エラーが発生したらスクリプトを終了

# ==== 変数定義 ====
RANDOM_INT=$(shuf -i 1-9999 -n 1)
LOCATION="westus"  
RESOURCE_GROUP_NAME="azure-ai-agent-handson-$RANDOM_INT"

# PostgreSQL/CosmosDB
PG_SERVER_NAME="pgserver-$RANDOM_INT"
PG_DB_NAME="ecdb"
PG_ADMIN_USER="ecadmin"
PG_ADMIN_PASS="YourP@ssword123!"
COSMOS_ACCOUNT_NAME="cosmos-$RANDOM_INT"
COSMOS_DB_NAME="twitterdb"
COSMOS_CONTAINER_NAME="reviews"
COSMOS_PARTITION_KEY="/user_name"
COSMOS_DB_THROUGHPUT=400

# AI Foundry
AI_FOUNDRY_NAME="foundry-$RANDOM_INT"
AI_PROJECT_NAME="${AI_FOUNDRY_NAME}-proj"
AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"

# Azure OpenAI
AZURE_OPENAI_NAME="aoai-$RANDOM_INT"
EMBEDDING_MODEL_NAME="text-embedding-ada-002"

# 追加リソース(Blob, AI Search, Logic Apps, Grounding with Bing)
BLOB_STORAGE_NAME="blob$RANDOM_INT"
AI_SEARCH_NAME="aisearch-$RANDOM_INT"
LOGIC_APP_NAME="logicapp-$RANDOM_INT"
BING_SEARCH_NAME="bingsearch-$RANDOM_INT"
# ==== リソースグループ作成 ====
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# ==== Bicep でデプロイ ====
az deployment group create \
  --resource-group $RESOURCE_GROUP_NAME \
  --name main \
  --template-file ./infra/main.bicep \
  --parameters \
      location=$LOCATION \
      pgServerName=$PG_SERVER_NAME \
      pgDbName=$PG_DB_NAME \
      pgAdminUser=$PG_ADMIN_USER \
      pgAdminPassword=$PG_ADMIN_PASS \
      cosmosAccountName=$COSMOS_ACCOUNT_NAME \
      cosmosDbName=$COSMOS_DB_NAME \
      cosmosContainerName=$COSMOS_CONTAINER_NAME \
      cosmosPartitionKey=$COSMOS_PARTITION_KEY \
      cosmosDbThroughput=$COSMOS_DB_THROUGHPUT \
      aiFoundryName=$AI_FOUNDRY_NAME \
      aiProjectName=$AI_PROJECT_NAME \
      aiModelDeploymentName=$AI_MODEL_DEPLOYMENT_NAME \
      azureOpenAIName=$AZURE_OPENAI_NAME \
      embeddingModelName=$EMBEDDING_MODEL_NAME \
      aiSearchName=$AI_SEARCH_NAME \
      blobStorageName=$BLOB_STORAGE_NAME \
      logicAppName=$LOGIC_APP_NAME \
      bingSearchName=$BING_SEARCH_NAME \
  --no-prompt --debug

# ==== DB 接続情報取得 ====
PG_HOST=$(az postgres flexible-server show \
  --name "$PG_SERVER_NAME" \
  --resource-group "$RESOURCE_GROUP_NAME" \
  --query "fullyQualifiedDomainName" -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP_NAME \
  --type keys \
  --query "primaryMasterKey" -o tsv)
COSMOS_URI="https://${COSMOS_ACCOUNT_NAME}.documents.azure.com:443/"

# ==== Azure AI Search 情報取得 ====
AI_SEARCH_ENDPOINT="https://${AI_SEARCH_NAME}.search.windows.net"
AI_SEARCH_KEY=$(az search admin-key show \
  --service-name $AI_SEARCH_NAME \
  --resource-group $RESOURCE_GROUP_NAME \
  --query "primaryKey" -o tsv)

# ==== Blob Storage 情報取得 ====
BLOB_STORAGE_KEY=$(az storage account keys list \
  --account-name $BLOB_STORAGE_NAME \
  --resource-group $RESOURCE_GROUP_NAME \
  --query "[0].value" -o tsv)

# ==== Azure OpenAI 情報取得 ====
AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $AZURE_OPENAI_NAME \
  --resource-group $RESOURCE_GROUP_NAME \
  --query "properties.endpoint" -o tsv)

AZURE_OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $AZURE_OPENAI_NAME \
  --resource-group $RESOURCE_GROUP_NAME \
  --query "key1" -o tsv)

echo "PG_HOST: $PG_HOST"
echo "COSMOS_URI: $COSMOS_URI"
echo "COSMOS_KEY: $COSMOS_KEY"
echo "AI_SEARCH_ENDPOINT: $AI_SEARCH_ENDPOINT"
echo "AI_SEARCH_KEY: $AI_SEARCH_KEY"
echo "BLOB_STORAGE_NAME: $BLOB_STORAGE_NAME"
echo "BLOB_STORAGE_KEY: $BLOB_STORAGE_KEY"
echo "AZURE_OPENAI_NAME: $AZURE_OPENAI_NAME"
echo "AZURE_OPENAI_ENDPOINT: $AZURE_OPENAI_ENDPOINT"
echo "AZURE_OPENAI_KEY: $AZURE_OPENAI_KEY"
echo "EMBEDDING_MODEL_NAME: $EMBEDDING_MODEL_NAME"
echo "LOGIC_APP_NAME: $LOGIC_APP_NAME"
echo "BING_SEARCH_NAME: $BING_SEARCH_NAME"

# ==== .env ファイル作成と更新 ====
# .env ファイルの作成
cp ./.env-sample .env

# .envの特定のキーを書き換える関数
update_env() {
  local key=$1
  local value=$2
  if grep -q "^$key=" .env; then
    sed -i "s|^$key=.*|$key=\"$value\"|" .env
  else
    # .env末尾が改行で終わっていない場合は改行する
    tail -c1 .env | read -r _ || echo >> .env
    echo "$key=\"$value\"" >> .env
  fi
}

update_env "AZURE_DEPLOYMENT_NAME" "$AI_MODEL_DEPLOYMENT_NAME"
update_env "PG_HOST" "$PG_HOST"
update_env "PG_USER" "$PG_ADMIN_USER"
update_env "PG_DB" "$PG_DB_NAME"
update_env "PG_PASS" "$PG_ADMIN_PASS"
update_env "COSMOS_ENDPOINT" "$COSMOS_URI"
update_env "COSMOS_KEY" "$COSMOS_KEY"
update_env "COSMOS_DB" "$COSMOS_DB_NAME"
update_env "COSMOS_CONTAINER" "$COSMOS_CONTAINER_NAME"
update_env "AI_SEARCH_ENDPOINT" "$AI_SEARCH_ENDPOINT"
update_env "AI_SEARCH_KEY" "$AI_SEARCH_KEY"
update_env "AZURE_OPENAI_ENDPOINT" "$AZURE_OPENAI_ENDPOINT"
update_env "AZURE_OPENAI_KEY" "$AZURE_OPENAI_KEY"
update_env "AZURE_DEPLOYMENT_NAME" "$AI_MODEL_DEPLOYMENT_NAME"


# ==== DB へデータ投入 ====
echo "# --- PostgreSQL テーブル作成＆CSV投入 ---"
python ./infra/import_to_db_scripts/import_csv_to_postgres.py "$PG_HOST" "$PG_DB_NAME" "$PG_ADMIN_USER" "$PG_ADMIN_PASS" "./infra/sample_data/to_postgresql/"

echo "# --- Cosmos DB (NoSQL) へtweets.json投入 ---"
python ./infra/import_to_db_scripts/import_jsonl_to_cosmos.py "$COSMOS_URI" "$COSMOS_KEY" "$COSMOS_DB_NAME" "$COSMOS_CONTAINER_NAME" "./infra/sample_data/to_cosmosdb/"

echo "done"
echo "== 準備完了！=="
