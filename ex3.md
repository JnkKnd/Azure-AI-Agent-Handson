# 演習 3 : 要約エージェント、Plannner エージェント、 Selector エージェントの作成

この演習 3 で実施するタスクは以下のとおりです。
- 要約エージェントの作成
- Planner エージェントの作成
- Selector エージェントの作成

## 演習 3-0 AutoGen について
- Azure AI Agent SDK で構築したシングルエージェントの構成をベースに、 AutoGen のマルチエージェント構成に書き換えていきます
- 

## 演習 3-1 contract_lookup_agent.py の作成

## 演習 3-2 product_search_agent.py の作成

## 演習 3-3 summary_agent.py の作成
要約エージェントはプロンプトを工夫して自分で実装してみてください。
Copilot なども活用してください。

## 演習 3-4 planner_agent.py の作成

## 演習 3-5 Selector Group Chat の作成
- 作成した各エージェントをモジュールとして読み込みます
```　python
from agents.contract_lookup_agent import contract_lookup_agent
from agents.product_search_agent import product_search_agent
from agents.summary_agent import summary_agent
from agents.planner_agent import planner_agent
```

<br>

## 次へ

👉 [**演習 4  :**](Ex01-1.md) 

<br>

<hr>

🏚️ [README に戻る](README.md)