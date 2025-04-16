# 演習 1 : 保険商品案内エージェントの作成

この演習 1 で実施するタスクは以下のとおりです。
- RAG 用インデックスの作成
- エージェントの作成
- インデックスをツールとして呼び出せるように登録
- Code Interpreter の登録
- Bing Search Grounding の登録
- エージェントからツールの呼び出し

![alt text](../images/image11.png)


## 演習 1-1 保険商品に関するインデックスを作成する
この演習では、保険商品の情報を Azure AI Search で検索できるように、インデックスを作成します。

---
### 1. サンプルデータをダウンロード

以下のサンプルデータを使用します。ダウンロードしてください。：

📄 [sampledata/product_info.md](../sampledata/product_info.md)

---

### 2. サンプルデータを Azure Storage にアップロード

手順：

1. Azure Portal にログイン。
2. Azure AI Foundry Hub を作成したときに一緒に作成された Storage Account を開く  
   ![image01-01](../images/image01-01.png)
3. `sampledata` という名前の Blob コンテナ を作成
   ![image01-02](../images/image01-02.png)
4. `product_info.md` をそのコンテナにアップロードする
   ![image01-03](../images/image01-03.png)

---

### 3. Azure AI Search でインデックスを作成

Azure AI Search のポータルで以下の手順に従ってインデックスを作成します：

1. Azure AI Search をデプロイする
   ![image01-04](../images/image01-04.png)
> **注意事項：**  
> - Azure AI Search の価格プランは **Free** を利用可能  
> - リージョンは **Azure AI Foundry Hub** と同一にしてください

2. RBAC（ロールベースアクセス制御）の手動設定

Azure AI Search からストレージにアクセスするには、以下の設定が必要です：

対象：**Azure AI Foundry Hub と同時に作成された Storage Account**

設定手順：  
1. Azure Portal > ストレージアカウント > 「アクセス制御（IAM）」へ移動
2. 「ロールの割り当て」から「Storage Blob データ閲覧者」を選択
   ![image01-10](../images/image01-10.png)
   ![image01-11](../images/image01-11.png)
3. 検索フィルタから Azure AI Search の マネージドID を選択
4. 「マネージド ID」リストから、Azure AI Search のリソース名（例：aisearch-xxx）を検索して選択
   ![image01-12](../images/image01-12.png)
5. すべての設定を確認した後、「**レビューと割り当て**」をクリックして、設定を完了。

これで、Azure AI Search がストレージアカウントにアクセスできるようになります。
この設定により、検索インデックス作成時に必要なストレージデータにアクセス可能となり、エージェントや他のアプリケーションから適切にデータを操作できます。 

3.「データのインポートとベクター化」を選択
   Azure AI Search のリソースに移動し、上部にあるデータのインポートとベクター化を選択してください。
   ![image01-05](../images/image01-05.png)
4. データソースで「Azure Blob Storage」を選択  
5. 先ほどアップロードした `product_info.md` を格納したストレージとコンテナを指定  
   ![image01-06](../images/image01-06.png)


## 演習 1-2 Grounding with Bing Search の作成  

### Grounding with Bing Search の作成

ここでは、「Grounding with Bing Search」リソースを新規作成します。
1. これまで使用していたサブスクリプション／リソースグループを選択
2. 「名前」には接続名として使いたい任意の文字列を入力（例：`agentdev04`）
3. 規約に同意し、「確認と作成」でデプロイ完了
![image01-07](../images/image01-07.png)

### プロジェクトに接続
1. AI Foundryでこれまで使用していたプロジェクトを選択し、管理センターを選択
![image01-13](../images/image01-13.png)
2. 「新しい接続」を選択し、「Bing検索を使用したグラウンド」を追加する。
![image01-14](../images/image01-14.png)
3. 管理画面に戻り、接続名を確認する。この追加方法の場合、既定でリソース名が接続名となります。
![image01-15](../images/image01-15.png)

 
## 演習1-3  動作確認

### .env ファイルの設定

以下のように `.env` ファイルの環境変数に接続名を指定してください：
```python
PROJECT_CONNECTION_STRING = <プロジェクトの接続文字列>
AI_SEARCH_ENDPOINT＝ <Azure AI Search のエンドポイント>
AI_SEARCH_KEY = <Azure AI Search のプライマリキー>
INDEX_NAME = <インデックス名>
BING_CONNECTION_NAME= <Bing 接続名> #(例 agentdev04) 
```

エージェントの作成からツールセットの登録、スレッドの実行までの手順は以下のノートブックから行ってください。

📄[product_search_agent.ipynb](../single-agent/product_search_agent.ipynb)


<br>

## 次へ

👉 [**演習2 : 契約管理エージェントの作成**](ex2.md) 

<br>

<hr>

🏚️ [README に戻る](README.md)
