import requests
import json
import os
from typing import Any, Callable, Set, Dict, List, Optional
from azure.ai.projects.models import FunctionTool, ToolSet
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient


def contract_lookup(user_id: int)->str:
    # 便宜上一旦ハードコードしています
    """
    ユーザーIDに基づいてユーザー情報を JSON 文字列で返す

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
        }
    }
    user_info = mock_users.get(user_id, {"error": "User not found."})
    return json.dumps({"user_info": user_info})


def send_email(customer:str, staff_email:str, inquiry: str)->str:
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
    headers = {'Content-Type': 'application/json'}
    payload = {
        "customer": customer,
        "inquiry": inquiry,
        "staff_email": staff_email
    }

    endpoint_url = os.getenv("LOGIC_APPS")

    try:
        response = requests.post(endpoint_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() 
        status = json.dumps({"status": "メールで通知が完了しました"})
        return status
    except requests.exceptions.RequestException as err:
        print(f"エラー: {err}")
        return json.dumps({"status": "メールで通知に失敗しました"})

# tool 登録方法の変更
user_functions: Set[Callable[..., Any]] = {
    contract_lookup,
    send_email
}

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

def contract_lookup_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    agent = AssistantAgent(
        name="ContractLookupAgent",
        description="顧客のデータを確認し、保険の契約状況と担当者を確認するエージェント。さらにユーザーからリクエストがあった場合、ユーザーの担当者に連絡をする。",
        model_client=model_client,
        tools = toolset,
        system_message="""丁寧に返してください""",
    )
    return agent
