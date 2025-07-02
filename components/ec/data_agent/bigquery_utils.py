import functools

from dotenv import load_dotenv
from google.cloud import bigquery

from lib.bigquery_client import bigquery_client

from .utils import ExtendedBaseModel

load_dotenv()

GOOGLE_CLOUD_PROJECT_ID = "bigquery-public-data"
BIGQUERY_DATASET_NAME = "thelook_ecommerce"
OUTPUT_DIRECTORY = "tmp"


class ColumnInfo(ExtendedBaseModel):
    column_name: str
    data_type: str
    is_nullable: bool
    ordinal_position: int


class TableInfo(ExtendedBaseModel):
    table_name: str
    columns: list[ColumnInfo]


class TablesInfo(ExtendedBaseModel):
    tables: list[TableInfo]


@functools.cache
def get_tables_info() -> TablesInfo:
    query = f"""
SELECT
  table_name,
  column_name,
  data_type,
  is_nullable,
  ordinal_position
FROM
  `{GOOGLE_CLOUD_PROJECT_ID}.{BIGQUERY_DATASET_NAME}.INFORMATION_SCHEMA.COLUMNS`
ORDER BY
  table_name,
  ordinal_position;
    """
    df = bigquery_client.query(query).to_dataframe()

    tables = {}
    for _, row in df.iterrows():
        table_name = row["table_name"]
        column_info = ColumnInfo(
            column_name=row["column_name"],
            data_type=row["data_type"],
            is_nullable=(row["is_nullable"].upper() == "YES"),
            ordinal_position=row["ordinal_position"],
        )
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append(column_info)

    return TablesInfo(
        tables=[
            TableInfo(table_name=table, columns=columns)
            for table, columns in tables.items()
        ]
    )


def dry_run_sql(sql: str) -> float:
    """Dry run a SQL query and return the estimated cost in MB."""
    result = bigquery_client.query(
        sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    )
    return result.total_bytes_processed / 1024 / 1024
