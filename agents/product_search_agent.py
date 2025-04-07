import json
import os
import datetime
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from typing import Any, Callable, Set, Dict, List, Optional
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient, VectorizedQuery
from openai import AzureOpenAI

"""
model client を引数に定義する
"""

# 環境変数の読み込み
load_dotenv()
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")

search_client = SearchClient(
    endpoint=AI_SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(AI_SEARCH_KEY)
)

def nonewlines(s: str) -> str:
    return s.replace("\n", " ").replace("\r", " ").replace("[", "【").replace("]", "】")

# Azure AI Search による検索
def search_product_info(query: str) -> str:
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
    search_product_info
}


functions = FunctionTool(user_functions)
# コードインタープリター
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)
