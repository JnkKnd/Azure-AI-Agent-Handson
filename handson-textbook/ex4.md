# 演習 4 : AutoGen でのマルチエージェント実装(後編)

この演習 4 で実施するタスクは以下のとおりです。
- app.py の作成
- chainlit による UI 作成

## app.py の作成
### 作成したエージェントをモジュールとしてインポート
- agents ディレクトリと同じ階層に app.py を作成してください
- 各種必要な AutoGen のモジュールをインポートします
- app.py の先頭にコピペしてください
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

- 作成した各エージェントをモジュールとして読み込みます
```　python
from agents.contract_lookup_agent import contract_lookup_agent
from agents.product_search_agent import product_search_agent
from agents.summary_agent import summary_agent
from agents.planner_agent import planner_agent
```

<br>

## 次へ

👉 [**演習5: エージェントの実装における考慮点**](ex5.md) 

<br>

<hr>

🏚️ [README に戻る](../README.md)