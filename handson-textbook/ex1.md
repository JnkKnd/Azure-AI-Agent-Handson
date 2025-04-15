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

2. 「データのインポートとベクター化」を選択  
   ![image01-05](../images/image01-05.png)
3. データソースで「Azure Blob Storage」を選択  
4. 先ほどアップロードした `product_info.md` を格納したストレージとコンテナを指定  
   ![image01-06](../images/image01-06.png)

---

### 4. RBAC（ロールベースアクセス制御）の手動設定

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

---

## 演習 1-2 エージェントの作成からツールセットの登録、スレッドの実行までの手順

このインデックス作成が完了したら、次の演習では AI Agent からこのデータを検索する処理を実装していきます。

### 1. セットアップ手順
1. VS Code 上で `single agents` フォルダを作成。
2. 下記のノートブックファイル（`product_search_agent.ipynb`）をそのフォルダ内に配置。

📄[product_search_agent.ipynb](../single-agent/product_search_agent.ipynb)

### 2.  補足：関数の定義
**Bing Search Grounding の接続名（Connection Name）の設定手順**

このノートブックでは、Bing 検索を利用するために **Grounding with Bing Search** を事前に作成し、  
それをエージェントのナレッジソースとして接続する必要があります。  
![image01-09](../images/image01-09.png)

接続時に入力する 「名前」 が、そのままコード内で使用する 接続名（Connection Name） になります。

---

**設定手順**
**Grounding with Bing Search の作成**

ここでは、「Grounding with Bing Search」を新規作成します。
1. これまで使用していたサブスクリプション／リソースグループを選択
2. 「名前」には接続名として使いたい任意の文字列を入力（例：`agentdev04`）
3. 規約に同意し、「確認と作成」でデプロイ完了
![image01-07](../images/image01-07.png)

**このとき指定した名前（例：`agentdev04`）が、コード内の接続名として使われます。**

---

#プロジェクトに接続

---

**ノートブック内での設定（参考）**
以下のように環境変数に接続名を指定してください： # env ファイルで変更

BING_CONNECTION_NAME=agentdev04

  
### 3.  動作の確認
- ターミナルからの実行
- エージェントプレイグラウンドでの確認

<br>

## 次へ

👉 [**演習2 : 契約管理エージェントの作成**](ex2.md) 

<br>

<hr>

🏚️ [README に戻る](README.md)
