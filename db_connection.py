"""
Database Connection Module - Stub for backward compatibility
This is a minimal implementation for the old SQL Server connection
"""
from loguru import logger


class DatabaseConnection:
    """Stub database connection for backward compatibility"""

    def __init__(self):
        """Initialize database connection (stub)"""
        logger.warning("DatabaseConnection stub initialized - not connected to any database")
        self.connected = False

    def execute_query(self, query: str, params: dict = None):
        """
        Execute SQL query (stub)

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Empty list (stub implementation)
        """
        logger.warning("DatabaseConnection.execute_query called on stub - returning empty results")
        return []

    def close(self):
        """Close database connection (stub)"""
        pass
