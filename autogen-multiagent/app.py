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

from contract_lookup_agent import contract_lookup_agent
from product_search_agent import product_search_agent
from summary_agent import summary_agent
from planner_agent import planner_agent

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
async def clean_console(stream):
    async for message in stream:
        if hasattr(message, "source") and hasattr(message, "content"):
            if message.source in [
                "SummaryAgent",
                "ProductSearchAgent",
                "ContractLookupAgent",
                "PlannerAgent",
            ]:
                print(f"\n---------- {message.source} ----------")
                print(message.content)

@cl.on_message
async def main(message: cl.Message) -> None:
    task = message.content

    try:
        # Run the async generator and collect the results
        stream = team.run_stream(task=task)

        if not hasattr(stream, "__aiter__"):
            raise TypeError("Expected an async generator, but got a non-iterable object.")

        async for message in stream:
            if isinstance(message, TaskResult):
                print(f"TaskResult: {message.stop_reason}")
                # await cl.Message(content=f"Final Output: {message.stop_reason}").send()
            elif isinstance(message, TextMessage):
                response = {"source": message.source, "text": message.content}
                print(f"TextMessage: {message.source}: {message.content}")
                await cl.Message(content=f"{message.source}: \n {message.content}").send()
            elif isinstance(message, ToolCallRequestEvent):
                print(f"ToolCall: {message}")
                await cl.Message(
                    content=f"エージェント: {message.source} \n 呼び出すツール: {message.content[0].name} \n パラメータ: {message.content[0].arguments} "
                ).send()
            elif isinstance(message, ToolCallExecutionEvent):
                print(f"ToolCall: {message}")
                await cl.Message(
                    content=f"エージェント: {message.source} \n ツール呼び出し結果: {message.content[0].content.encode().decode('unicode_escape')} "
                ).send()
    except TypeError as e:
        print(f"Error: {e}")
        await cl.Message(content=f"Error: {e}").send()
