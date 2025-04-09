import json
import os
import datetime
from dotenv import load_dotenv
from typing import Any, Callable, Set
from azure.identity import DefaultAzureCredential
from azure.core import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient
from azure.ai.projects.models import FunctionTool, ToolSet, BingGroundingTool, MessageTextContent
from azure.ai.projects import AIProjectClient


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
    endpoint=AI_SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(AI_SEARCH_KEY),
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
        query_type="semantic",  # セマンティック検索を有効化
        semantic_configuration_name="insurance-product-info-semantic-configuration",  # セマンティック検索用の構成名（環境に合わせて変更
        top=3,  # 上位5件を取得（必要に応じて変更）
    )
    context = [nonewlines(doc["chunk"]) for doc in results]
    context_json = json.dumps({"context": context})
    print(context_json)
    return context_json


# ユーザ関数のセットアップ
user_functions: Set[Callable[..., Any]] = {product_search}

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)
toolset.add(bing)

agent = project_client.agents.create_agent(
    model="gpt-4o-mini",
    name="Product Search Agent",
    instructions="""
あなたは、丁寧なアシスタントです。あなたは以下の業務を遂行します。
- 保険の商品について検索して回答します
- Bing 検索でインターネットの情報を検索して回答します
- Code Interpreter でコードの生成および実行を行います

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
    thread_id=thread.id, agent_id=agent.id
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

# project_client.agents.delete_thread(thread_id=thread.id)
# project_client.agents.delete_agent(agent_id=agent.id)
