import time
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from config import Config

# Mock Database Schema Blueprint for Failover (In-Memory Fallback)
MOCK_FALLBACK_SCHEMA = [
    {
        "table_name": "users",
        "column_name": "id",
        "data_type": "integer",
        "is_nullable": "NO",
        "constraints": "PRIMARY KEY"
    },
    {
        "table_name": "users",
        "column_name": "email",
        "data_type": "character varying",
        "is_nullable": "NO",
        "constraints": "UNIQUE"
    },
    {
        "table_name": "users",
        "column_name": "password_hash",
        "data_type": "character varying",
        "is_nullable": "NO",
        "constraints": "None"
    },
    {
        "table_name": "api_logs",
        "column_name": "id",
        "data_type": "uuid",
        "is_nullable": "NO",
        "constraints": "PRIMARY KEY"
    },
    {
        "table_name": "api_logs",
        "column_name": "headers",
        "data_type": "jsonb",
        "is_nullable": "YES",
        "constraints": "None"
    }
]

# Strict Read-Only Metadata Query (Zero Row-Data Exposure)
METADATA_QUERY = """
SELECT 
    cols.table_name,
    cols.column_name,
    cols.data_type,
    cols.character_maximum_length,
    cols.is_nullable,
    COALESCE(string_agg(DISTINCT cons.constraint_type, ', '), '') as constraints
FROM 
    information_schema.columns cols
LEFT JOIN 
    information_schema.key_column_usage kcu 
    ON cols.table_schema = kcu.table_schema 
    AND cols.table_name = kcu.table_name 
    AND cols.column_name = kcu.column_name
LEFT JOIN 
    information_schema.table_constraints cons 
    ON kcu.table_schema = cons.table_schema 
    AND kcu.table_name = cons.table_name 
    AND kcu.constraint_name = cons.constraint_name
WHERE 
    cols.table_schema = 'public'
GROUP BY 
    cols.table_name, 
    cols.column_name, 
    cols.data_type, 
    cols.character_maximum_length, 
    cols.is_nullable, 
    cols.ordinal_position
ORDER BY 
    cols.table_name, 
    cols.ordinal_position;
"""

def parse_schema_to_markdown(raw_rows: List[Dict[str, Any]]) -> str:
    """
    Groups columns by table name and compiles a readable, token-efficient
    Markdown schema documentation map for Gemini models.
    """
    if not raw_rows:
        return "### No public tables found in the database."

    tables: Dict[str, List[Dict[str, Any]]] = {}
    for row in raw_rows:
        table_name = row["table_name"]
        if table_name not in tables:
            tables[table_name] = []
        tables[table_name].append(row)

    markdown_parts = ["# Database Schema Blueprints\n"]
    for table_name, columns in tables.items():
        markdown_parts.append(f"## Table: `{table_name}`")
        markdown_parts.append("| Column | Data Type | Nullable | Constraints |")
        markdown_parts.append("| :--- | :--- | :--- | :--- |")
        for col in columns:
            col_name = col["column_name"]
            
            # Format type representation (include length if applicable)
            data_type = col.get("data_type", "unknown")
            max_len = col.get("character_maximum_length")
            type_str = f"{data_type}({max_len})" if max_len else data_type
            
            nullable = "YES" if col.get("is_nullable") == "YES" else "NO"
            constraints = col.get("constraints") or col.get("constraint_type") or "None"
            
            markdown_parts.append(f"| `{col_name}` | `{type_str}` | `{nullable}` | `{constraints}` |")
        markdown_parts.append("")  # Empty line separator

    return "\n".join(markdown_parts)

def get_database_schema() -> str:
    """
    Fetches PostgreSQL schema metadata using read-only query logic,
    retrying 3 times with exponential backoff on connection errors,
    and falling back to an in-memory mock schema if all retries fail.
    """
    # Verify environment values are supplied, if not fallback immediately
    if not all([Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD]):
        print("[DB Failover] Configs incomplete. Falling back to Mock Schema Blueprint.")
        return parse_schema_to_markdown(MOCK_FALLBACK_SCHEMA)

    max_retries = 3
    backoff_delay = 0.5
    conn = None

    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                connect_timeout=2
            )
            # Enforce read-only transaction state on this connection session as a failsafe
            conn.set_session(readonly=True, autocommit=True)
            
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(METADATA_QUERY)
                rows = [dict(row) for row in cursor.fetchall()]
                return parse_schema_to_markdown(rows)
                
        except (psycopg2.OperationalError, psycopg2.InterfaceError) as conn_err:
            print(f"[DB Connect Attempt {attempt}/{max_retries}] Operational error occurred: {conn_err}")
            if attempt == max_retries:
                print("[DB Connect Failover] Max retries reached. Returning in-memory fallback schema.")
                return parse_schema_to_markdown(MOCK_FALLBACK_SCHEMA)
            time.sleep(backoff_delay)
            backoff_delay *= 2
        except Exception as other_err:
            print(f"[DB Connect Attempt {attempt}/{max_retries}] Unexpected error: {other_err}")
            return parse_schema_to_markdown(MOCK_FALLBACK_SCHEMA)
        finally:
            if conn:
                conn.close()

