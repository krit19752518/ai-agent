import unittest
from unittest.mock import patch, MagicMock
import psycopg2

import sys
import os
# Ensure import path is set correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, "src")
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from mcp.db_schema import get_database_schema, MOCK_FALLBACK_SCHEMA, parse_schema_to_markdown
from config import Config

class TestDBSchemaRetryFailover(unittest.TestCase):
    
    def setUp(self):
        # Backup original DB configurations
        self.original_db_name = Config.DB_NAME
        self.original_db_user = Config.DB_USER
        self.original_db_password = Config.DB_PASSWORD
        
        # Configure valid dummy configs to pass the get_database_schema preliminary checks
        Config.DB_NAME = "test_db"
        Config.DB_USER = "test_user"
        Config.DB_PASSWORD = "test_password"

    def tearDown(self):
        # Restore original configs
        Config.DB_NAME = self.original_db_name
        Config.DB_USER = self.original_db_user
        Config.DB_PASSWORD = self.original_db_password

    @patch("psycopg2.connect")
    def test_database_connection_success_first_attempt(self, mock_connect):
        # Mock database connection and query response
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        
        # Return mock database rows representing schema metadata
        mock_cursor.fetchall.return_value = [
            {"table_name": "users", "column_name": "id", "data_type": "integer", "is_nullable": "NO", "constraints": "PRIMARY KEY"}
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = get_database_schema()
        
        # Verify psycopg2.connect was called exactly once
        mock_connect.assert_called_once()
        self.assertIn("Table: `users`", result)
        self.assertIn("`id`", result)

    @patch("psycopg2.connect")
    @patch("time.sleep") # Mock sleep to prevent test delay during exponential backoff
    def test_database_connection_failover_on_operational_error(self, mock_sleep, mock_connect):
        # Force psycopg2.connect to raise OperationalError for all 3 attempts
        mock_connect.side_effect = psycopg2.OperationalError("Connection refused")

        result = get_database_schema()

        # Check if connect was called exactly 3 times due to retries
        self.assertEqual(mock_connect.call_count, 3)
        # Check if fallback mock schema markdown is returned
        expected_fallback_markdown = parse_schema_to_markdown(MOCK_FALLBACK_SCHEMA)
        self.assertEqual(result, expected_fallback_markdown)
        # Ensure exponential backoff was slept
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("psycopg2.connect")
    @patch("time.sleep")
    def test_database_connection_success_on_third_attempt(self, mock_sleep, mock_connect):
        # Fail first 2 attempts, succeed on the 3rd attempt
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"table_name": "users", "column_name": "id", "data_type": "integer", "is_nullable": "NO", "constraints": "PRIMARY KEY"}
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_connect.side_effect = [
            psycopg2.OperationalError("Timeout 1"),
            psycopg2.OperationalError("Timeout 2"),
            mock_conn
        ]

        result = get_database_schema()

        self.assertEqual(mock_connect.call_count, 3)
        self.assertIn("Table: `users`", result)
        self.assertEqual(mock_sleep.call_count, 2)

if __name__ == "__main__":
    unittest.main()
