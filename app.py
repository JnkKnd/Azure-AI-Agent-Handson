import json
import os
import datetime
import logging
import chainlit as cl
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MessageTextContent
from openai import AzureOpenAI
from autogen import Agent, AssistantAgent

from agents.contract_lookup_agent import contract_lookup_agent
#from agents.product_search_agent import product_search_agent
#from agents.summary_agent import summary_agent
#from agents.planner_agent import planner_agent
#from agents.selector_agent import get_team

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

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)

aoai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version="2025-01-01-preview",
)

contract_lookup_agent = contract_lookup_agent(aoai_client)

"""
# Agent の共有 Wrapperクラス
class ChainlitLoggableAgent(AssistantAgent):
    async def send(
        self, message, recipient, request_reply: bool = None, silent: bool = False
    ):
        # Chainlit に中間出力を表示
        await cl.Message(
            content=f"【{self.name}】{message} → {recipient.name}", author=self.name
        ).send()
        # 元の送信処理を呼び出す
        return await super().send(
            message, recipient, request_reply=request_reply, silent=silent
        )


# UI
@cl.on_chat_start
async def initialize_team():
    team = get_team(aoai_client)

    await cl.Message(content="エージェントチームを起動しました。タスクを入力してください。").send()
    # ユーザーメッセージを起点に各エージェントで対話を進行させる処理を書く
    # 例: チャット初期入力を team に渡すなど
    user_input = await cl.AskUserMessage(content="タスクを入力してください", timeout=60)
    # チーム全体に対して対話を開始、または最初のエージェント（PlannerAgent）にメッセージを送る
    await team.initiate(user_input["content"])

@cl.on_message
async def main(user_message: str):
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="Handson Chat Agent",
        instructions="",
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

"""
