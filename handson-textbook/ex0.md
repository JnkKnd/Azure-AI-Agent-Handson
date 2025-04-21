## 目次
0. [事前準備とリソースの作成](ex0.md)
1. [保険商品案内エージェントの作成](ex1.md)
2. [契約管理エージェントの作成](ex2.md)
3. [AutoGen でのマルチエージェント実装(前編)](ex3.md)
4. [AutoGen でのマルチエージェント実装(後編)](ex4.md)
5. [マルチエージェントの実装における考慮点](ex5.md)

## 演習 0-1 : 開発環境の確認
### 必要事項
  - Visual Studio Code の確認
  - Azure Subscription の確認
  - python version の確認 (3.11 推奨)
    - 3.11 以下のバージョンをお使いの場合、[Python 3.11.0](https://www.python.org/downloads/release/python-3110/)をダウンロードしてください
    - インストーラー実行の際は 「Add Python 3.11 to PATH」 にチェックを必ず入れてください


### ローカルでの開発環境のセットアップ
※ 下記は Windows Powershell の場合の例です。コマンドは環境に応じて適宜読みかえてください。


1. リポジトリをクローン
    ```
    git clone https://github.com/JnkKnd/Azure-AI-Agent-Handson.git
    ```

1. ディレクトリに移動
    ```
    cd ./Azure-AI-Agent-Handson
    ```

1. 仮想環境を作成（python の version は 3.11 以上をお使いください）\
    ```
    py -3.11 -m venv .venv
    ```
    3.11 以下のバージョンをお使いの場合、[Python 3.11.0](https://www.python.org/downloads/release/python-3110/)をダウンロードしてください。\
インストーラー実行の際は 「Add Python 3.11 to PATH」 にチェックを必ず入れてください。
1. 仮想環境を有効化
    ```
    ./.venv/Scripts/activate.ps1
    ``` 
    コマンド実行後、powershell では左端に (.venv)と表示されます

1. python の version を確認
    ```
    python --version
    ```
    ここで python 3.11 系が表示されればOKです。

1. pip を最新にします
    ```
    python -m pip install --upgrade pip
    ```

1. 必要なライブラリをインストール
    ```
    pip install -r ./requirements.txt
    ```

1. `.env-sample`をコピーし、同じ階層に `.env`ファイルとして保存
    ```
    copy .env-sample .env
    ```

### ディレクトリの構造について
今回のハンズオンのディレクトリ構造は下記の通りです。
```
.
└── Azure-AI-Agent-Handson\
    ├── autogen-multiagent\
    │   ├── autogen-multiagent.ipynb 演習3で用いるノートブック\
    │   └── (略)\
    ├── handson-textbook\ 
    │   ├── ex0.md 演習0\
    │   ├── ex1.md 演習1\
    │   ├── ex2.md 演習2\
    │   ├── ex3.md 演習3\
    │   ├── ex4.md 演習4\
    │   └── ex5.md 演習5\
    ├── sampledata\
    │   ├── users サンプルのユーザーデータが入っているフォルダ\
    │   ├── code-interpreter-sample コードインタープリターで生成される画像のサンプル\
    │   └── product_info.md 保険商品のサンプルデータ\
    ├── single-agent\
    │   ├── contract_lookup_agents.ipynb 演習2で用いるノートブック\
    │   └── product_search_agents.ipynb　演習1で用いるノートブック\
    └── sk-multiagent\
        └── sk-multiagent.ipynb Semantic Kernel を勉強するノートブック
```


## 演習 0-2 : 事前準備とリソースの作成
この演習 0 で実施するタスクは以下のとおりです。
- リソースの作成
  - Azure AI Foundry Hub
  - Azure AI Foundry Project
    - gpt-4o-2024-08-06 のデプロイ

また、演習中に作成するリソースは以下の通りです。
  - Azure AI Search (S0 or Basic)
  - Bing Grounding Tool
  - Logic Apps
  - Cosmos DB

### Azure AI Foundry の作成
1. [Azure portal](https://portal.azure.com/) にアクセスして「リソースの作成」をクリックします。\
  ![alt text](../images/image02.png)

1. 上部のテキストボックスに「Azure AI Foundry」と入力して検索します。以下のように Azure AI Foundry が表示されたら作成をクリックします。仮に２つ表示された場合、下記画像と同じものから作成してください。\
  ![alt text](../images/image03.png)

2. 必要事項を以下のように入力して「確認および作成」をクリックします。\
※今回は「**West US**」リージョンに作成します。\

| 項目               | 値                                      |
|--------------------|------------------------------------------|
| サブスクリプション | ご自身が使う予定のサブスクリプション     |
| リソースグループ   | 新規作成を選択し、任意のリソースグループ名をつける |
| リージョン         | West US                                 |
| リソースの名前     | 任意                          |
| OpenAI を含む AI サービスに接続する| 新規作成を選択し、任意のリソース名をつける|

3. その他の設定はデフォルト値のままで構いません。[確認および作成]を押下し、内容を確認して問題なければ[作成]をクリックします。


    以下のリソースが自動的に新規作成されます。

    - Azure AI Foundry ハブ
    - Azure AI services
      - (Azure OpenAI Service もこの Azure AI Service に含まれます)
    - Storage Account
    - キー コンテナー


4. リソースのデプロイが完了したら、リソースへ移動し「Launch Azure AI Foundry」をクリックします。

### Azure AI Foundry プロジェクトの作成
1. Azure AI Foundry を起動したら、最上位階層「ハブ」に新しいプロジェクトを作成します。以下のように「新しいプロジェクト」ボタンをクリックします。\
  ![alt text](../images/image04.png)

1. 任意のプロジェクト名を入力して「プロジェクトを作成する」をクリックします。\
  UI が異なる場合がございますが、ハブの欄に先ほど作成した Azure AI Foundry Hub リソースが作成されていればOKです。
  ![alt text](../images/image05.png)

1. プロジェクトが作成されます。これでプロジェクトごとにエージェントを構築・管理できるようになります。ここで、後続の手順のために、プロジェクトの接続文字列をメモしておきます。プロジェクトの概要欄にある、接続文字列をコピーします。
  ![alt text](../images/image010.png)

1. メモ帳などにメモをしておくか、 `.env`ファイルに直接追記してもOKです。
    ```
    PROJECT_CONNECTION_STRING="コピーした接続文字列"
    ```


### Azure OpenAI モデルのデプロイ
1. 左のメニューの下部にある[マイアセット]内の[モデル＋エンドポイント]を選択して[モデルのデプロイ]を選択し、[基本モデルをデプロイする]をクリックします。

1. 今回は `gpt-4o` のモデルバージョン `2024-08-06` を使用します。（Grounding with Bing に対応しているモデルのため ）以下のようにモデルを選択し「確認」ボタンをクリックします。\
  ![alt text](../images/image06.png)

1.  以下のようにデプロイ設定を行います。デプロイの種類は「グローバル標準」に設定します。特に同一リージョン内に他の Azure OpenAI リソースがある場合はクォータキャップに注意してください。 「デプロイの詳細」の右上にある「カスタマイズ」を選択し、モデルバージョンを 「2024-08-06」に指定してください。また「1分あたりのトークン数レート制限」の値が小さい場合は引き上げてください。50K程度あれば十分です。
  ![alt text](../images/image07.png)

「デプロイ」ボタンをクリックするとすぐにデプロイされます。

1. ここで、Azure OpenAI のエンドポイントとキー、メモの


### Embedding モデルのデプロイ
`gpt-4o` のデプロイ時と同様に、`text-embedding-ada-002` をデプロイします。このモデルは演習1で、保険商品に関するサンプルデータから Azure AI Search でインデックスを作成する際に必要になります。

1. 左のメニューの下部にある「マイアセット」内の「モデル＋エンドポイント」を選択して「モデルのデプロイ」を選択し、「基本モデルをデプロイする」をクリックします。

1. `text-embedding-ada-002` のモデルを選択します。以下のようにモデルを選択し「確認」ボタンをクリックします。
  ![alt text](../images/image08.png)

1.  デプロイ設定は、デフォルト値のままで構いません。デプロイの種類は「グローバル標準」に設定します。
  ![alt text](../images/image09.png)

「デプロイ」ボタンをクリックするとすぐにデプロイされます。

演習0はこれで終了です。Azure AI Foudry でモデルを利用する準備ができました。\
次は Azure AI Agent Service についての座学を行ったのち、演習1でシングルエージェントを実装していきます。


<br>

## 次へ

👉 [**演習1：保険商品案内エージェントの作成**](ex1.md)

<br>

<hr>

🏚️ [README に戻る](../README.md)