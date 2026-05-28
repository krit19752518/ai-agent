import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from src.config import Config

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
    Fetches PostgreSQL schema metadata using read-only query logic
    and returns a Markdown table representation of all tables.
    """
    # Verify environment values are supplied
    if not all([Config.DB_NAME, Config.DB_USER, Config.DB_PASSWORD]):
        return (
            "Error: Database configurations are incomplete.\n"
            "Please check DB_NAME, DB_USER, and DB_PASSWORD in environment variables."
        )

    conn = None
    try:
        # Establish connection with PostgreSQL (Read-Only context should be enforced at DB-user privilege level)
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=5
        )
        
        # Enforce read-only transaction state on this connection session as a failsafe
        conn.set_session(readonly=True, autocommit=True)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(METADATA_QUERY)
            rows = [dict(row) for row in cursor.fetchall()]
            return parse_schema_to_markdown(rows)
            
    except Exception as e:
        return f"Failed to retrieve database schema: {str(e)}"
    finally:
        if conn:
            conn.close()
