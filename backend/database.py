import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/northwind"
)

engine = create_engine(DATABASE_URL)


def get_engine():
    return engine


def get_schema_info() -> str:
    """
    Reads live schema from PostgreSQL information_schema.
    Returns a formatted string the LLM can understand.
    """
    query = text("""
        SELECT
            c.table_name,
            c.column_name,
            c.data_type,
            CASE WHEN pk.column_name IS NOT NULL THEN 'PRIMARY KEY' ELSE '' END AS key_type
        FROM information_schema.columns c
        LEFT JOIN (
            SELECT kcu.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public'
        ) pk ON c.table_name = pk.table_name AND c.column_name = pk.column_name
        WHERE c.table_schema = 'public'
        ORDER BY c.table_name, c.ordinal_position;
    """)

    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()

    if not rows:
        return "No tables found in the public schema."

    schema_lines = []
    current_table = None
    for table_name, column_name, data_type, key_type in rows:
        if table_name != current_table:
            if current_table is not None:
                schema_lines.append("")
            schema_lines.append(f"Table: {table_name}")
            schema_lines.append("-" * (len(table_name) + 7))
            current_table = table_name
        key_marker = f" [{key_type}]" if key_type else ""
        schema_lines.append(f"  {column_name} ({data_type}){key_marker}")

    return "\n".join(schema_lines)


def execute_query(sql: str) -> dict:
    """
    Validates and executes a SQL SELECT query.
    Returns rows and column names.
    Blocks dangerous statements.
    """
    sql_upper = sql.strip().upper()
    dangerous = ["DROP", "DELETE", "TRUNCATE", "INSERT", "UPDATE",
                 "ALTER", "CREATE", "GRANT", "REVOKE"]
    for keyword in dangerous:
        if keyword in sql_upper:
            raise ValueError(
                f"Blocked: '{keyword}' statements are not allowed. "
                "Only SELECT queries are permitted."
            )

    if not sql_upper.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")

    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

    return {"columns": columns, "rows": rows, "row_count": len(rows)}
