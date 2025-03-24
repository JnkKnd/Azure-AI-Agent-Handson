import json
import os
import datetime
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
from azure.search.documents import SearchClient, VectorizedQuery
from openai import AzureOpenAI

"""
model client を引数に定義する
"""

# 環境変数の読み込み
load_dotenv()
PROJECT_CONNECTION_STRING = os.getenv('PROJECT_CONNECTION_STRING')
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
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# Azure AI Search による検索
def search_product_info(user_query: str)-> str :
    """
    Get the current time as a JSON string, optionally formatted.

    :param format (Optional[str]): 時刻のフォーマット。指定がない場合は "%Y-%m-%d %H:%M:%S" を使用
    :return: Json フォーマットの現在時刻
    :rtype: str
    """

    vector_query = aoai_client.embeddings.create(
        input=[user_query], model=EMBEDDING_MODEL
    ).data[0].embedding

    retrieved_docs = search_client.search(
        search_text=user_query,
        vector_queries=[vector_query],
        top=3,
        highlight_fields="content-3",
        select=["sourcepage", "content", "category"],
        query_type="semantic",
        semantic_configuration_name="default",
    )

    semantic_answers = retrieved_docs.get_answers()
    print("semantic answer = ", semantic_answers)
    for answer in semantic_answers:
        if answer.highlights:
            print(f"Semantic Answer: {answer.highlights}")
        else:
            print(f"Semantic Answer: {answer.text}")
        print(f"Semantic Answer Score: {answer.score}\n")

    for doc in retrieved_docs:
        captions = doc["@search.captions"]
        if captions:
            caption = captions[0]
            if caption.highlights:
                print(f"Caption: {caption.highlights}\n")
            else:
                print(f"Caption: {caption.text}\n")

    return None


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
