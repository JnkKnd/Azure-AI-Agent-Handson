import os
import json
import asyncio
import asyncpg
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime
from fastmcp import FastMCP
from azure.cosmos import CosmosClient

load_dotenv()

# PostgreSQL 接続情報
PG_CONFIG = {
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASS"),
    "database": os.getenv("PG_DB"),
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PGPORT", 5432)),
}

# CosmosDB 接続情報
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB", "twitterdb")
COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "tweets")

# MCP サーバ定義
mcp = FastMCP(
    name="Retail Shop + Twitter Analytics",
    instructions="PostgreSQLの各種マスター、注文、ユーザー情報と、CosmosDBに格納されたツイート分析データを、ツールとして提供します。"
)

# PostgreSQL 共通ヘルパ
async def get_conn():
    return await asyncpg.connect(**PG_CONFIG)

def to_json(data):
    return json.dumps(data, ensure_ascii=False, default=str)

# CosmosDB 共通ヘルパ
def get_cosmos_container():
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    db = client.get_database_client(COSMOS_DB_NAME)
    return db.get_container_client(COSMOS_CONTAINER_NAME)

# --- PostgreSQL Tools ---
@mcp.tool(
    name="get_all_categories",
    description="""
        全カテゴリ一覧を取得します。

        :return: JSON形式でカテゴリの一覧を返します。
        :rtype: str
    """,
    tags=["postgres"]
)
async def get_all_categories() -> str:
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT * FROM categories")
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_all_users",
    description="""
        全ユーザー一覧を取得します。

        :return: JSON形式でユーザーの一覧を返します。
        :rtype: str
    """
)
async def get_all_users() -> str:
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT * FROM users")
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_products_by_category",
    description="""
        指定カテゴリIDで絞り込んだ商品の一覧を取得します。

        :param category_id (int): 商品カテゴリID（必須）
        :rtype: str

        :return: JSON形式で商品の一覧を返します。
        :rtype: str
    """
)
async def get_products_by_category(category_id: int) -> str:
    conn = await get_conn()
    try:
        rows = await conn.fetch(
            "SELECT * FROM products WHERE category_id = $1", category_id
        )
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_orders_by_user",
    description="""
        特定ユーザーの注文一覧を取得します。

        :param user_id (int): ユーザーID
        :rtype: str

        :return: JSON形式で注文の一覧を返します。
        :rtype: str
    """
)
async def get_orders_by_user(user_id: int) -> str:
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT * FROM orders WHERE user_id = $1", user_id)
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_order_details",
    description="""
        注文詳細を取得します。

        :param order_id (int): 注文ID
        :rtype: str

        :return: JSON形式で注文詳細情報を返します。
        :rtype: str
    """
)
async def get_order_details(order_id: int) -> str:
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT * FROM order_details WHERE order_id = $1", order_id)
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_sales_by_category",
    description="""
        指定した期間（開始日～終了日）でカテゴリ別の売上集計（上位10件）を取得します。

        :param start_date (str): 集計開始日（YYYY-MM-DD）
        :param end_date (str): 集計終了日（YYYY-MM-DD）
        :rtype: str

        :return: JSON形式でカテゴリID,カテゴリ名,売上金額のリストを返します。
        :rtype: str
    """
)
async def get_sales_by_category(
    start_date: str,
    end_date: str
) -> str:
    conn = await get_conn()
    try:
        sql = """
            SELECT
                c.category_id,
                c.category_name,
                SUM(od.price * od.quantity) AS total_sales
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            JOIN categories c ON p.category_id = c.category_id
            JOIN orders o ON od.order_id = o.order_id
            WHERE TO_DATE(o.order_date, 'YYYY-MM-DD') >= TO_DATE($1, 'YYYY-MM-DD')
              AND TO_DATE(o.order_date, 'YYYY-MM-DD') <= TO_DATE($2, 'YYYY-MM-DD')
            GROUP BY c.category_id, c.category_name
            ORDER BY total_sales DESC
            LIMIT 10
        """
        rows = await conn.fetch(sql, start_date, end_date)
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()

@mcp.tool(
    name="get_sales_by_product",
    description="""
        指定した期間（開始日～終了日）で商品別の売上集計（上位10件）を取得します。

        :param start_date (str): 集計開始日（YYYY-MM-DD）
        :param end_date (str): 集計終了日（YYYY-MM-DD）
        :rtype: str

        :return: JSON形式でproduct_id, product_name, total_salesのリストを返します。
        :rtype: str
    """
)
async def get_sales_by_product(
    start_date: str,
    end_date: str
) -> str:
    conn = await get_conn()
    try:
        sql = """
            SELECT
                p.product_id,
                p.product_name,
                SUM(od.price * od.quantity) AS total_sales
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            JOIN orders o ON od.order_id = o.order_id
            WHERE TO_DATE(o.order_date, 'YYYY-MM-DD') >= TO_DATE($1, 'YYYY-MM-DD')
              AND TO_DATE(o.order_date, 'YYYY-MM-DD') <= TO_DATE($2, 'YYYY-MM-DD')
            GROUP BY p.product_id, p.product_name
            ORDER BY total_sales DESC
            LIMIT 10
        """
        rows = await conn.fetch(sql, start_date, end_date)
        return to_json([dict(r) for r in rows])
    finally:
        await conn.close()


# --- CosmosDB Tools ---
@mcp.tool(
    name="get_review_summary",
    description="""
        商品ごと、もしくは全体のレビューを集計します。

        :param product_id (int, Optional): 商品ID。指定しない場合は全商品が対象。
        :rtype: str

        :return: JSON形式でレビューの集計結果（product_id, review_count, avg_rating, pos_count, neg_countなど）。
        :rtype: str
    """
)
async def get_review_summary(product_id: Optional[int] = None) -> str:
    container = get_cosmos_container()
    query = "SELECT c.product_id, c.rating, c.recommend, c.tags FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    # フィルタ
    if product_id is not None:
        items = [i for i in items if i.get("product_id") == product_id]
    if not items:
        return to_json({"review_count": 0, "avg_rating": None, "pos_count": 0, "neg_count": 0})
    review_count = len(items)
    avg_rating = sum(i["rating"] for i in items) / review_count
    pos_count = sum(1 for i in items if i["rating"] >= 4)
    neg_count = sum(1 for i in items if i["rating"] <= 2)
    return to_json({
        "product_id": product_id,
        "review_count": review_count,
        "avg_rating": round(avg_rating, 2),
        "pos_count": pos_count,
        "neg_count": neg_count,
    })

@mcp.tool(
    name="get_top_products_by_review",
    description="""
        レビュー評価が高い順に商品ランキング（上位10件）を取得します。

        :return: JSON形式で product_id, avg_rating, review_count のリストを返します。
        :rtype: str
    """
)
async def get_top_products_by_review() -> str:
    container = get_cosmos_container()
    query = "SELECT c.product_id, c.rating FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    # 商品ごとに集計
    from collections import defaultdict
    d = defaultdict(list)
    for i in items:
        if i.get("product_id") is not None:
            d[i["product_id"]].append(i["rating"])
    result = []
    for pid, ratings in d.items():
        avg_rating = sum(ratings) / len(ratings)
        result.append({"product_id": pid, "avg_rating": round(avg_rating,2), "review_count": len(ratings)})
    # 上位10件
    top10 = sorted(result, key=lambda x: (-x["avg_rating"], -x["review_count"]))[:10]
    return to_json(top10)

@mcp.tool(
    name="get_trending_tags",
    description="""
        最近使われているタグやワードランキングを集計して返します。

        :param top_n (int, Optional): 上位いくつまで返すか。デフォルト10。
        :rtype: str

        :return: JSON形式で tag, count のリストを返します。
        :rtype: str
    """
)
async def get_trending_tags(top_n: int = 10) -> str:
    container = get_cosmos_container()
    query = "SELECT c.tags FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    from collections import Counter
    all_tags = []
    for i in items:
        if i.get("tags"):
            all_tags.extend(i["tags"])
    counts = Counter(all_tags)
    return to_json([{"tag": tag, "count": count} for tag, count in counts.most_common(top_n)])


@mcp.tool(
    name="get_reviews_by_period_and_product",
    description="""
        指定した期間内かつ指定商品のレビュー（詳細）一覧を取得します。

        :param start_date (str): 集計開始日（YYYY-MM-DD）
        :param end_date (str): 集計終了日（YYYY-MM-DD）
        :param product_name (str, Optional): 商品名で絞り込み。未指定の場合は全商品。
        :rtype: str

        :return: JSON形式で {review_date, product_id, product_name, rating, comment, user_id など} のリストを返します。
    """
)
async def get_reviews_by_period_and_product(
    start_date: str,
    end_date: str,
    product_name: Optional[str] = None,
) -> str:
    container = get_cosmos_container()
    query = "SELECT c.product_id, c.product_name, c.review_date, c.rating, c.comment, c.user_id FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    # フィルタ処理
    filtered = []
    for i in items:
        # 日付・商品名フィルタ
        if not i.get("review_date"):
            continue
        if i["review_date"] < start_date or i["review_date"] > end_date:
            continue
        if product_name and i.get("product_name") != product_name:
            continue
        filtered.append(i)
    # 新しい順（または必要に応じてソート）
    result = sorted(filtered, key=lambda x: x["review_date"], reverse=True)
    return to_json([
        {
            "review_date": i["review_date"],
            "product_id": i.get("product_id"),
            "product_name": i.get("product_name"),
            "rating": i.get("rating"),
            "comment": i.get("comment"),
            "user_id": i.get("user_id"),
        } for i in result
    ])


# --- サーバ起動 ---
if __name__ == "__main__":
    asyncio.run(mcp.run(transport="http", host="0.0.0.0", port=8000))
