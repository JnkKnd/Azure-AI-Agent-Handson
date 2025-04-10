import json
import os
import logging
import asyncio
import chainlit as cl
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_agentchat.teams import BaseGroupChat, SelectorGroupChat
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TaskResult

from agents.contract_lookup_agent import contract_lookup_agent
from agents.product_search_agent import product_search_agent
from agents.summary_agent import summary_agent
from agents.planner_agent import planner_agent

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.openai import OpenAIInstrumentor

logging.getLogger("autogen_agentchat").setLevel(logging.ERROR)
logging.getLogger("autogen_ext.models.openai").setLevel(logging.ERROR)

# 環境変数の読み込み
load_dotenv()
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_CRED = os.getenv("AI_SEARCH_CRED")

aoai_client = AzureOpenAIChatCompletionClient(
    azure_deployment=DEPLOYMENT_NAME,
    model="gpt-4o",
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)


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

## 会話履歴

{history}
"""


# SelectorGroupChat:共有コンテキストに基づいて次のスピーカーを選択
planner = planner_agent(aoai_client)
product_search = product_search_agent(aoai_client)
contract_lookup = contract_lookup_agent(aoai_client)
summary = summary_agent(aoai_client)

termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

team = SelectorGroupChat(
    [
        planner,
        product_search,
        contract_lookup,
        summary,
    ],
    model_client=aoai_client,
    termination_condition=termination_condition,
    selector_prompt=selector_prompt,
    allow_repeated_speaker=False,
)

# task = "2025年おすすめの旅行先を推薦してください。"

async def main() -> None:
    task = input("タスクを入力してください： ")
    # task = user_message

    # Run the async generator and collect the results
    stream = team.run_stream(task=task)
    await Console(stream)

asyncio.run(main())
