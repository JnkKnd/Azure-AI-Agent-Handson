"""
実装してみてください。
"""
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient

def summary_agent(model_client: ChatCompletionClient) -> AssistantAgent:

    sumamry_agent = AssistantAgent(
        name="SummaryAgent",
        description="これまでの会話履歴を要約する AI アシスタント",
        model_client=model_client,
        system_message="""
あなたのタスクは、他の team members が収集した情報をもとに、これまでの会話履歴の要約を作成することです。

## 回答ルール

- ユーザーからの質問に対して、他の team member が収集した情報を使って適切な回答を作成してください。
- 作成後、最終回答の文章の最後に "TERMINATE" と入力して、タスクを完了します。
"""
    )

    return sumamry_agent