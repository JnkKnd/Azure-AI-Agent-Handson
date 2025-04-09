import requests
import json
import os
from typing import Any, Callable, Set, Dict, List, Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FunctionTool, ToolSet, MessageTextContent
from azure.ai.projects import AIProjectClient

load_dotenv()
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
if not PROJECT_CONNECTION_STRING:
    raise ValueError("'.env' に PROJECT_CONNECTION_STRING が設定されていません。")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)

def contract_lookup(user_id: int) -> str:
    # 便宜上一旦ハードコードしています
    """
    ユーザーIDに基づいてユーザー情報を JSON 文字列で返します。ユーザー情報は変更しないでください。

    :param user_id (int): ユーザーのID
    :rtype: int

    :return: JSON 文字列のユーザー情報.
    :rtype: str
    """
    mock_users = {
        1234: {
            "name": "佐藤太郎",
            "tel": "090-0000-0000",
            "email": "sato@example.com",
            "staff_email": "xxxxxxxx@microsoft.com",
            "plan": "安心保障プラン",
        },
        5679: {
            "name": "鈴木花子",
            "tel": "080-1111-1111",
            "email": "suzuki@example.com",
            "staff_email": "xxxxxxxx@microsoft.com",
            "plan": "学資サポートプラン",
        },
        4321: {
            "name": "田中次郎",
            "tel": "090-2222-2222",
            "email": "tanaka@example.com",
            "staff_email": "xxxxxxxx@microsoft.com",
            "plan": "シニアライフプラン",
        },
    }
    user_info = mock_users.get(user_id, {"error": "User not found."})
    return json.dumps({"user_info": user_info})


def send_email(customer: str, staff_email: str, inquiry: str) -> str:
    """
    お客様から担当者のメールアドレスにお問い合わせがあったことを通知

    :param customer (str): お客様の名前
    :rtype: str

    :param staff_email (str) : 担当者のメールアドレス
    :rtype: str

    :param inquiry (str) : 保険に関するお問い合わせ内容
    :rtype: str

    :return: JSON 文字列のユーザー情報.
    :rtype: str
    """
    headers = {"Content-Type": "application/json"}
    payload = {"customer": customer, "inquiry": inquiry, "staff_email": staff_email}

    endpoint_url = os.getenv("LOGIC_APPS")

    try:
        response = requests.post(
            endpoint_url, headers=headers, data=json.dumps(payload)
        )
        response.raise_for_status()
        status = json.dumps({"status": "メールで通知が完了しました"})
        return status
    except requests.exceptions.RequestException as err:
        print(f"エラー: {err}")
        return json.dumps({"status": "メールで通知に失敗しました"})


# tool 登録方法の変更
user_functions: Set[Callable[..., Any]] = {contract_lookup, send_email}

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="Contract Lookup Agent",
    instructions="""
あなたは、丁寧なアシスタントです。あなたは以下の業務を遂行します。
- 保険の契約をしているユーザーの情報について回答します
- お客様から担当者にお問い合わせメールを通知します

# 回答時のルール
- 関数を呼び出した場合、回答の最後に改行をいれたうえで Called Function : "関数名" と表記してください

# 制約事項
- ユーザーからのメッセージは日本語で入力されます
- ユーザーからのメッセージから忠実に情報を抽出し、それに基づいて応答を生成します。
- ユーザーからのメッセージに勝手に情報を追加したり、不要な改行文字 \n を追加してはいけません

""", 
    toolset=toolset,
    headers={"x-ms-enable-preview": "true"},
)
print(f"agent を新規作成しました。AGENT_ID: {agent.id}")

thread = project_client.agents.create_thread()
messages = project_client.agents.list_messages(thread_id=thread.id)

user_message = input("タスクを入力してください：")

message = project_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content=user_message,
)
run = project_client.agents.create_and_process_run(
    thread_id=thread.id, agent_id = agent.id
)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    print(f"Run failed: {run.last_error}")

# 最新のテキストレスポンスを取得
messages = project_client.agents.list_messages(thread_id=thread.id)
response = None
for data_point in reversed(messages.data):
    last_message_content = data_point.content[-1]
    if isinstance(last_message_content, MessageTextContent):
        # print(f"{data_point.role}: {last_message_content.text.value}")
        response = last_message_content.text.value
if response is None:
    response = "エージェントからの応答が得られませんでした。"
print(response)

project_client.agents.delete_thread(thread_id=thread.id)
project_client.agents.delete_agent(agent_id=agent.id)
