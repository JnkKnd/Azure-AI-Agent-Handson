import sys
import os
import glob
import pandas as pd
import psycopg2
from psycopg2 import sql

def infer_postgres_type(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return 'INTEGER'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'TIMESTAMP'
    else:
        return 'TEXT'

def main(pg_host, pg_db, pg_user, pg_pass, csv_dir):
    conn = psycopg2.connect(
        host=pg_host, dbname=pg_db, user=pg_user, password=pg_pass
    )
    cursor = conn.cursor()

    for csv_file in glob.glob(os.path.join(csv_dir, '*.csv')):
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        df = pd.read_csv(csv_file)

        # テーブル作成SQL生成
        columns = []
        for col in df.columns:
            dtype = infer_postgres_type(df[col])
            columns.append(f'"{col}" {dtype}')
        create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(columns)});'
        cursor.execute(create_table_sql)
        conn.commit()

        # TRUNCATE（洗い替え：テーブルを空にする）
        cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY;')
        conn.commit()

        # データ投入
        col_names = ','.join([f'"{c}"' for c in df.columns])
        for _, row in df.iterrows():
            placeholders = ','.join(['%s'] * len(row))
            insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
            cursor.execute(insert_sql, tuple(row))
        conn.commit()
        print(f'Inserted {len(df)} rows into {table_name}')

    cursor.close()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage: python import_csv_to_postgres.py <PG_HOST> <PG_DB> <PG_USER> <PG_PASS> <CSV_DIR>')
        sys.exit(1)
    main(*sys.argv[1:])
