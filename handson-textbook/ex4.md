# 演習 4 : AutoGen でのマルチエージェント実装(後編)

この演習 4 で実施するタスクは以下のとおりです。
- app.py を作成し、GroupChat 部分を実装
- chainlit による簡易的な UI 作成

## app.py の作成
### 作成したエージェントをモジュールとしてインポート
1. agents ディレクトリと同じ階層に app.py を作成してください
1. 各種必要な AutoGen のモジュールをインポートします
1. app.py の先頭に以下を記述してください。これ以降のコードは下に足していってください。
```　python
import json
import os
import chainlit as cl
from dotenv import load_dotenv
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TaskResult
from autogen_agentchat.messages import TextMessage,ToolCallExecutionEvent, ToolCallRequestEvent
```

- 前編で作成した4つのエージェントをモジュールとして読み込みます
```　python
from agents.contract_lookup_agent import contract_lookup_agent
from agents.product_search_agent import product_search_agent
from agents.summary_agent import summary_agent
from agents.planner_agent import planner_agent
```

### 環境変数の読み込み
```python
load_dotenv()
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_CRED = os.getenv("AI_SEARCH_CRED")
```

### LLM クライアントの定義
```python
aoai_client = AzureOpenAIChatCompletionClient(
    azure_deployment=DEPLOYMENT_NAME,
    model="gpt-4o",
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)
```

### Selector Group Chat 作成時のプロンプト指定
```python
selector_prompt = """あなたのタスクは、会話の状況に応じて次のタスクを実行する role を選択することです。
## 次の話者の選択ルール

各 role の概要以下です。

{roles}

次のタスクに選択可能な participants は以下です。

{participants}

以下のルールに従って、次のを選択してください。

- 会話履歴を確認し、次の会話に最適な role を選択します。role name のみを返してください。
- role は1つだけ選択してください。
- 他の role が作業を開始する前に、"PlannerAgent" にタスクを割り当て、サブタスクを計画してもらうことが必要です。
  - PlannerAgent はサブタスクの計画のみを行います。サブタスクの作業を依頼してはいけません。
- PlannerAgent が計画したサブタスクに応じて、role を選択します。
- タスクを完了するための必要な情報が揃ったと判断したら "SummaryAgent" に最終回答の作成を依頼します。
```

### 各エージェントに、モデルクライアントを引数に渡す
```python
planner = planner_agent(aoai_client)
product_search = product_search_agent(aoai_client)
contract_lookup = contract_lookup_agent(aoai_client)
summary = summary_agent(aoai_client)
```

### マルチエージェントの終了条件を定義します
```python
```

### 各エージェントに、モデルクライアントを引数に渡す
```python
```

### 各エージェントに、モデルクライアントを引数に渡す
```python
```

<br>

## 次へ

👉 [**演習5: エージェントの実装における考慮点**](ex5.md) 

<br>

<hr>

🏚️ [README に戻る](../README.md)