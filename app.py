import json
import os
import datetime
import logging
import chainlit as cl
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from typing import Any, Callable, Set, Dict, List, Optional
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FunctionTool,
    ToolSet,
    CodeInterpreterTool,
    AzureAISearchTool,
    BingGroundingTool,
    MessageTextContent,
)
from azure.search.documents import SearchClient
from openai import AzureOpenAI

core_logger = logging.getLogger("autogen_core")
core_logger.setLevel(logging.WARNING)

# 環境変数の読み込み
load_dotenv()
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_CRED = os.getenv("AI_SEARCH_CRED")


if not PROJECT_CONNECTION_STRING:
    raise ValueError("'.env' に PROJECT_CONNECTION_STRING が設定されていません。")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)
if not PROJECT_CONNECTION_STRING:
    raise ValueError("'.env' に PROJECT_CONNECTION_STRING が設定されていません。")


search_client = SearchClient(
    endpoint=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AI_SEARCH_CRED
)

aoai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
)


# UI 部分を担わせる
@cl.on_message
async def main(user_message: str):
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="Handson Chat Agent",
        instructions="""
        あなたは、丁寧なアシスタントです。あなたは以下の業務を遂行します。
        - 現在の時刻を回答します
        - 天気の情報を提供します
        - 保険の契約をしているユーザーの情報について回答します
        - 保険の商品について検索して回答します
        - お客様から担当者にお問い合わせメールを通知します

        # 回答時のルール
        - 関数を呼び出した場合、回答の最後に改行をいれたうえで Called Function : "関数名" と表記してください

        # 制約事項
        - ユーザーからのメッセージは日本語で入力されます
        - ユーザーからのメッセージから忠実に情報を抽出し、それに基づいて応答を生成します。
        - ユーザーからのメッセージに勝手に情報を追加したり、不要な改行文字 \n を追加してはいけません

        """,
        headers={"x-ms-enable-preview": "true"},
    )
    thread = project_client.agents.create_thread()
    messages = project_client.agents.list_messages(thread_id=thread.id)

    # セッションにエージェントIDとスレッドIDを保存
    cl.user_session.set("agent_id", agent.id)
    cl.user_session.set("thread_id", thread.id)

    print(f"Created agent, agent ID: {agent.id}, thread ID: {thread.id}\n")

    # セッションからエージェントIDとスレッドIDを取得
    agent_id = cl.user_session.get("agent_id")
    thread_id = cl.user_session.get("thread_id")
    if not agent_id or not thread_id:
        await cl.Message(
            "内部エラー: エージェントまたはスレッドが見つかりません。"
        ).send()
        return

    # ユーザーメッセージをスレッドに登録
    message = project_client.agents.create_message(
        thread_id=thread_id,
        role="user",
        content=user_message.content,
    )
    run = project_client.agents.create_and_process_run(
        thread_id=thread_id, agent_id=agent_id
    )
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # 最新のテキストレスポンスを取得
    messages = project_client.agents.list_messages(thread_id=thread_id)
    response = None
    for data_point in reversed(messages.data):
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")
            response = last_message_content.text.value
    if response is None:
        response = "エージェントからの応答が得られませんでした。"
    await cl.Message(response).send()


@cl.on_chat_end
def end_chat():
    # セッションからエージェントIDとスレッドIDを取得してクリーンアップ
    agent_id = cl.user_session.get("agent_id")
    thread_id = cl.user_session.get("thread_id")
    if thread_id:
        project_client.agents.delete_thread(thread_id=thread_id)
    if agent_id:
        project_client.agents.delete_agent(agent_id=agent_id)
    print(f"Deleted agent, agent ID: {agent_id}, thread ID: {thread_id}")


if __name__ == "__main__":
    cl.run()

