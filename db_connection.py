import os
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from loguru import logger
import urllib

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'sqlserver')
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '1433')
        self.database = os.getenv('DB_NAME', 'MarketingIQ')
        self.username = os.getenv('DB_USER', 'sa')
        self.password = os.getenv('DB_PASSWORD')

        self.engine = None
        self.connection = None

    def get_connection_string(self):
        """Get SQL Server connection string"""
        if self.db_type == 'sqlserver':
            params = urllib.parse.quote_plus(
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.host},{self.port};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'TrustServerCertificate=yes'
            )
            return f'mssql+pyodbc:///?odbc_connect={params}'
        else:
            return f'sqlite:///{self.database}.db'

    def get_engine(self):
        """Get SQLAlchemy engine"""
        if not self.engine:
            connection_string = self.get_connection_string()
            self.engine = create_engine(
                connection_string,
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
        return self.engine

    def get_pyodbc_connection(self):
        """Get direct pyodbc connection for bulk operations"""
        if self.db_type == 'sqlserver':
            conn_str = (
                f'DRIVER={{ODBC Driver 18 for SQL Server}};'
                f'SERVER={self.host},{self.port};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'TrustServerCertificate=yes'
            )
            return pyodbc.connect(conn_str)
        return None

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        engine = self.get_engine()
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            if result.returns_rows:
                return result.fetchall()
            conn.commit()
            return None

    def bulk_insert(self, table_name, data_frame, schema='dw'):
        """Bulk insert DataFrame into SQL Server table"""
        try:
            engine = self.get_engine()
            data_frame.to_sql(
                table_name,
                engine,
                schema=schema,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            logger.info(f"Bulk inserted {len(data_frame)} rows into {schema}.{table_name}")
            return True
        except Exception as e:
            logger.error(f"Error bulk inserting into {schema}.{table_name}: {e}")
            return False

    def test_connection(self):
        """Test database connection"""
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

# Singleton instance
db = DatabaseConnection()