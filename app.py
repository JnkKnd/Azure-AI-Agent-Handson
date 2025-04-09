import json
import os
import logging
import asyncio
import chainlit as cl
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_agentchat.teams import BaseGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console

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

service_name = "autogen"

# OTLPエクスポーターの設定 (gRPC経由で送信)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # JaegerのgRPCエンドポイント
)
tracer_provider = TracerProvider(resource=Resource({"service.name": service_name}))

# トレーサープロバイダーの設定
trace.set_tracer_provider(tracer_provider)

# バッチスパンプロセッサーを設定
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)

# トレーサーを取得
tracer = tracer_provider.get_tracer(service_name)
OpenAIInstrumentor().instrument()

core_logger = logging.getLogger("autogen_core")
core_logger.setLevel(logging.WARNING)

# 環境変数の読み込み
load_dotenv()
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_CRED = os.getenv("AI_SEARCH_CRED")

aoai_client = AzureAIChatCompletionClient(
    endpoint=AZURE_OPENAI_ENDPOINT,
    credential=AzureKeyCredential(AZURE_OPENAI_KEY),
    api_version="2025-01-01-preview",
    model_info={
        "json_output": False,
        "function_calling": True,
        "vision": False,
        "family": "gpt-4o",
        "structured_output": False,
        "deployment_name": DEPLOYMENT_NAME,
    },
)

# https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/selector-group-chat.html#selector-prompt

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

with tracer.start_as_current_span(
    "SelectorGroupChat"
) as rollspan:  # ルートスパンを作成

    # SelectorGroupChat:共有コンテキストに基づいて次のスピーカーを選択
    planner_agent = planner_agent(aoai_client)
    product_search_agent = product_search_agent(aoai_client)
    contract_lookup_agent = contract_lookup_agent(aoai_client)
    summary_agent = summary_agent(aoai_client)

    termination_condition = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

    team = SelectorGroupChat(
        [
            planner_agent,
            product_search_agent,
            contract_lookup_agent,
            summary_agent,
        ],
        model_client=aoai_client,
        termination_condition=termination_condition,
        selector_prompt=selector_prompt,
        allow_repeated_speaker=False,
    )

    # task = "2025年おすすめの旅行先を推薦してください。"
    task = input("タスクを入力してください： ")

    # Run the async function
    asyncio.run(Console(team.run_stream(task=task)))
