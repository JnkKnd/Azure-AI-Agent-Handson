import json
import os
import datetime
import logging
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
