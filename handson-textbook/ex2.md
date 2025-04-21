# 演習 2 : 契約管理エージェントの作成
この演習 2 で実施するタスクは以下のとおりです。
- Cosmos DB からユーザー情報を取得
- Logic Apps でメール送信を実行

![alt text](../images/image02-01.png)

## 演習 2-1 Logic Apps の作成
1. [Azure portal](https://portal.azure.com/) で、Azure アカウントを使ってサインイン
2. Azure portal の検索ボックスに「logic app」と入力し、[Logic Apps] を選択

![alt text](../images/image02-02.png)

3. [Add （もしくは「追加」）]を押下

4. 従量課金の「マルチテナント」を選択し、[選択] を押下

![alt text](../images/image02-03.png)

5. [基本] タブで、次の情報を入力

| プロパティ | 値 | 備考 |
| --- | ---| ---|
| サブスクリプション | <Azure サブスクリプション名> | |
| リソース グループ |<Azure リソース グループ名> ||
| ロジック アプリ名 |  <Logic Apps 名> ||
| リージョン |  <リージョン名> | |
| ログ分析を有効化 |  いいえ | |

> ※ 入力すると、設定は次の例のようになります。

![alt text](../images/image02-04.png)

6. [確認および作成] を押下し、問題なければ [作成] を押下
7. 正常にデプロイできたら、[リソースに移動] を選択
8. リソースに移動したら、開発ツール内の[ロジック アプリ デザイナー] を押下

![alt text](../images/image02-05.png)

9. [トリガーの追加] から [Request] を検索し、Request の [When a HTTP is received] を押下

10. [パラメータ] タブで、[Method] を「POST」に選択し、[Request Body JSON Schema] に以下のjsonをコピペ

```json
{
  "type": "object",
  "properties": {
    "customer": {
      "type": "string"
    },
    "inquiry": {
      "type": "string"
    },
    "staff_email": {
      "type": "string"
    }
  }
}
```
> ※ 完了すると、設定は次の例のようになります。

![alt text](../images/image02-06.png)

11. 「When a HTTP request is received」 ステップの後に、「＋」ボタンからアクションを追加

![alt text](../images/image02-20.png)

12. [メールを送信] を検索し、Outlook.com の [メールの送信（V2）] を選択

![alt text](../images/image02-08.png)

13. [サインイン] が求められるので、Microsoft アカウントでサインイン

> ※ （補足）Microsoft アカウントでサインインできない場合は、メール送信ステップを飛ばし、手順 15 に進んでください。

14. [パラメータ] タブで、次の情報を入力

![alt text](../images/image02-09.png)

> ※ 以下のように稲妻マークから前の手順のデータを引き継ぐことができます。
> ![alt text](../images/image02-29.png)

15. 入力が終わったら、「＋」ボタンからアクションを追加

![alt text](../images/image02-22.png)

16. [Response] を検索し、Request の [Response] を選択

![alt text](../images/image02-23.png)

17. Response アクションは以下のようにデフォルトのままでOK

![alt text](../images/image02-10.png)

18. [Save] を押下すると、[When a HTTP request is received] の 「HTTP URL」が発行されるためコピーしてメモしておく（後ほど使用）

![alt text](../images/image02-11.png)

> ※ メール送信を飛ばされた方は、最終的に以下のようになります。
> ![alt text](../images/image02-30.png)

## 演習 2-2 Cosmos DB for NoSQL の作成
1. Azure portal の検索ボックスに「Cosmos DB」と入力し、[Cosmos DB] を選択

![alt text](../images/image02-12.png)

2. [Add （もしくは「追加」）]を押下し、[Azure Cosmos DB for NoSQL] の [作成] を押下

![alt text](../images/image02-13.png)

3. [Basics（もしくは基本情報）] タブにて、以下のパラメータを入力し、[レビュー+作成] を押下

**プロジェクトの詳細**

| プロパティ | 値 | 備考 |
| --- | ---| ---|
| Workload Type | Development / Testing | |
| サブスクリプション | <Azure サブスクリプション名> | |
| リソース グループ |<Azure リソース グループ名> ||

**インスタンスの詳細**

| プロパティ | 値 | 備考 |
| --- | ---| ---|
| アカウント名 |  <Cosmos DB のアカウント名> ||
| Availability Zones | 無効 | |
| リージョン (場所) |  (US) West US 2 | |
| 容量モード | Serverless | |


> ※ 入力すると、設定は次の例のようになります。

![alt text](../images/image02-25.png)

4. 内容を確認し、問題なければ [作成] を押下。デプロイが完了するまで待機。

5. デプロイが完了したら、[リソースに移動] を押下

6. [データ エクスプローラー] を選択し、[New Container] を押下し、次のパラメータを入力し [OK] を押下

| プロパティ |  値 | 備考 |
| --- | ---|  ---|
| Database Id (Create new) | cosmicworks | |
| Container Id |  users ||
| Partition Key | /plan ||

※ 完了すると、設定は次の例のようになります。

![alt text](../images/image02-26.png)

7. データ エクスプローラーのツリーで、[users] コンテナーを展開し、[Items] を選択し、[New Item] を押下

![alt text](../images/image02-16.png)

8. 当リポジトリの `./sampledata/users` ディレクトリ配下の 3 つの `json` ファイルをローカルから選択してアップロード

![alt text](../images/image02-18.png)

アップロードが成功すると以下のようになります。

![alt text](../images/image02-17.png)

9. Items をリロードすると、各 Item が追加されているのを確認

![alt text](../images/image02-19.png)

10. 最後に、[設定] の中から [キー] を選択し、Cosmos DB の `URI` と `PRIMARY KEY` をメモしておく（後ほど使用）

![alt text](../images/image02-27.png)

## 演習 2-3 動作確認

### .env ファイルの設定
以下のように `.env` ファイルの環境変数に接続名を指定してください：
```python 
LOGIC_APPS= <Logic Apps の HTTP URL>
ACCOUNT_URI= <Cosmos DB の URI>
ACCOUNT_KEY= <Cosmos DB の アカウントキー>
```

次のノートブックから、動作確認を行ってください。

[contract_lookup_agent.ipynb](../single-agent/contract_lookup_agent.ipynb)

※ Connection Aborted といったエラーが出た場合は、もう一度実行を試してみてください。

<br>

## 次へ

👉 [**演習3 :AutoGen でのマルチエージェント実装(前編)**](ex3.md) 

<br>

<hr>

🏚️ [README に戻る](../README.md)