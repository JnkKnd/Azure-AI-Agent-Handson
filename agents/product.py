import json
import datetime
from dotenv import dotenv_values
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

# 環境変数の読み込み
load_dotenv()
PROJECT_CONNECTION_STRING = env_vars["PROJECT_CONNECTION_STRING"]
if not PROJECT_CONNECTION_STRING:
    raise ValueError("'.env' に PROJECT_CONNECTION_STRING が設定されていません。")


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=PROJECT_CONNECTION_STRING
)
