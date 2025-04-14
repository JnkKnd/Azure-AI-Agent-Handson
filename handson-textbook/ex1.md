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

以下のファイルを使用します：

📄 [sampledata/product_info.md](../sampledata/product_info.md)

---

### 2. サンプルデータを Azure Storage にアップロード

手順：

1. Azure Portal にログイン
2. Azure AI Foundry Hub を作成したときに一緒に作成された Storage Account を開く  
   ![image01-01](../images/image01-01.png)
3. `sampledata` という名前の **Blob コンテナ** を作成（または既存のコンテナにアップロード）  
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

## 4. RBAC（ロールベースアクセス制御）の手動設定

Azure AI Search からストレージにアクセスするには、以下の設定が必要です：

- 対象：**Azure AI Foundry Hub と同時に作成された Storage Account**
- 設定手順：  
  1. Azure Portal > ストレージアカウント > 「アクセス制御（IAM）」へ移動  
  2. 「ロールの割り当て」から「Storage Blob データ閲覧者」を選択  
  3. 検索フィルタから Azure AI Search の **マネージドID** を選択し、割り当て  
     ![image01-07](../images/image01-07.png)

---

## 次のステップへ

このインデックス作成が完了したら、次の演習では AI Agent からこのデータを検索する処理を実装していきます。


## 演習 1-2 保険商品案内エージェントの作成
1. VScode で single agents フォルダを作成する

## 演習 1-2 関数の定義
- Azure AI Search の検索
- Code Interpreter 追加
- Bing Search

## 演習 1-3 動作の確認
- ターミナルからの実行
- エージェントプレイグラウンドでの確認

<br>

## 次へ

👉 [**演習2 : 契約管理エージェントの作成**](ex2.md) 

<br>

<hr>

🏚️ [README に戻る](README.md)
