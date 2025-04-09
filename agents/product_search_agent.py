import json
import os
import datetime
from dotenv import load_dotenv
from typing import Any, Callable, Set, Dict, List, Optional
from azure.identity import DefaultAzureCredential
from azure.core import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient
from azure.ai.projects.models import FunctionTool, ToolSet, BingGroundingTool
from azure.ai.projects import AIProjectClient
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

"""
model client を引数に定義する
"""

# 環境変数の読み込み
load_dotenv()
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")

PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
BING_CONNECTION_NAME = os.getenv("BING_CONNECTION_NAME")

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

bing_connection = project_client.connections.get(connection_name=BING_CONNECTION_NAME)
bing_conn_id = bing_connection.id
# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=bing_conn_id)

search_client = SearchClient(
    endpoint=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(AI_SEARCH_KEY)
)

def nonewlines(s: str) -> str:
    return s.replace("\n", " ").replace("\r", " ").replace("[", "【").replace("]", "】")

# Azure AI Search による検索
def product_search(query: str) -> str:
    """
    保険の商品に関する質問に関して、Azure AI Search の検索結果を返します。

    :param query (str): 保険の商品を検索する際のクエリ
    :rtype: str

    :return: JSON 文字列の検索結果の情報
    :rtype: str
    """

    results = search_client.search(
        search_text=query,
        query_type="semantic",                      # セマンティック検索を有効化
        semantic_configuration_name="insurance-product-info-semantic-configuration",  # セマンティック検索用の構成名（環境に合わせて変更
        top=3                                       # 上位5件を取得（必要に応じて変更）
    )
    context = [nonewlines(doc['chunk']) for doc in results]
    context_json = json.dumps({"context": context})
    print(context_json)
    return context_json


# ユーザ関数のセットアップ
user_functions: Set[Callable[..., Any]] = {
    product_search
}

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
toolset.add(bing)


def product_search_agent(model_client: ChatCompletionClient) -> AssistantAgent:
    agent = AssistantAgent(
        name="ProductSearchAgent",
        description="顧客のデータを確認し、保険の契約状況と担当者を確認するエージェント。さらにユーザーからリクエストがあったばあい、ユーザーの担当者に連絡をする。",
        model_client=model_client,
        toolset=toolset,
        system_message="""丁寧に返してください""",
    )
    return agent
