import time
from typing import List

import pandas as pd
from sqlalchemy import create_engine, text, inspect
import urllib.parse


class AccessDatabaseManager:
    def __init__(self, driver='Microsoft Access Driver (*.mdb, *.accdb)', password=None, db_path=None):
        """
        Initialize the database manager
        :param db_path: Path to .accdb or .mdb file
        :param driver: ODBC driver name
        :param password: Database password (optional)
        """
        self.db_path = db_path
        self.driver = driver
        self.password = password
        self.engine = None
        self.connection = None
        self.input_table = None
        self.similarity_table = None
        self.output_table = None

    def connect(self, db_path=None):
        """Establish a connection to the database"""
        try:
            if db_path:
                self.db_path = db_path

            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"DBQ={self.db_path};"
            )

            if self.password:
                connection_string += f"PWD={self.password};"

            encoded_conn = urllib.parse.quote_plus(connection_string)
            self.engine = create_engine(f"access+pyodbc://?odbc_connect={encoded_conn}")
            self.connection = self.engine.connect()
            print("Connected to database successfully")
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            raise

    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.engine.dispose()
            print("Connection closed")
        else:
            print("No active connection to close")

    def execute_query(self, query, params=None):
        """
        Execute a write query (INSERT, UPDATE, DELETE)
        :param query: SQL query string
        :param params: Dictionary of parameters for parameterized queries
        :return: Number of rows affected
        """
        try:
            result = self.connection.execute(text(query), params)
            self.connection.commit()
            print(f"Query executed successfully. Rows affected: {result.rowcount}")
            return result.rowcount
        except Exception as e:
            print(f"Query failed: {str(e)}")
            raise

    def fetch_query(self, query, params=None) -> List[dict]:
        """
        Execute a read query (SELECT)
        :param query: SQL query string
        :param params: Tuple of parameters for parameterized queries
        :return: List of dictionaries representing rows
        """
        try:
            result = self.connection.execute(text(query), params)
            return [dict(zip(result.keys(), row)) for row in result.fetchall()]
        except Exception as e:
            print(f"Fetch failed: {str(e)}")
            raise

    def get_table_as_dataframe(self, table_name: str) -> pd.DataFrame:
        """
        Convert a database table to a pandas DataFrame.

        Args:
            table_name (str): Name of the table to convert

        Returns:
            pd.DataFrame: DataFrame containing the table data

        Raises:
            RuntimeError: If connection is not established
            ValueError: If table doesn't exist

        Example:
            >>> db_manager = AccessDatabaseManager("database.accdb")
            >>> db_manager.connect()
            >>> df = db_manager.get_table_as_dataframe("Customers")
        """
        if not self.engine:
            raise RuntimeError("Not connected to database. Call connect() first.")

        try:
            # Verify table exists first
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
                if result.scalar() == 0:
                    raise ValueError(f"Table {table_name} exists but contains no data")

            # Read full table
            return pd.read_sql_table(table_name, self.engine)

        except Exception as e:
            if "no such table" in str(e).lower():
                raise ValueError(f"Table {table_name} does not exist") from e
            raise RuntimeError(f"Failed to read table {table_name}: {str(e)}") from e

    def get_table_names(self):
        """Retrieve all table names from the database using an SQLAlchemy Engine object."""
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        return table_names


    def get_table_names(self):
        """
        Get all table names in the database
        :return: List of table names
        """
        if not self.engine:
            raise RuntimeError("Not connected to database. Call connect() first.")

        inspector = inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_columns(self, table_name):
        if table_name not in self.get_table_names():
            raise ValueError(f"Table name {table_name} doesn't exist")      
        else:
            df = pd.read_sql_table(table_name, con=self.engine)
            return df.columns

    def has_table(self, table_name):
        if table_name not in self.get_table_names():
            return False
        return True

    def set_input_table(self, table_name):
        if self.has_table(table_name):
            self.input_table = table_name
        else:
            raise ValueError(f"Table name {table_name} doesn't exist")

    def set_output_table(self, table_name):
        if self.has_table(table_name):
            self.output_table = table_name
        else:
            raise ValueError(f"Table name {table_name} doesn't exist")

    def set_similarity_table(self, table_name):
        if self.has_table(table_name):
            self.similarity_table = table_name
        else:
            raise ValueError(f"Table name {table_name} doesn't exist")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

class DBDaemon:
    def __init__(self, db_manager: AccessDatabaseManager, shared_data):
        self.db_manager = db_manager
        self.shared_data = shared_data
        pass

    def run(self):
        print("db daemon running")
        while True:
            if len(self.shared_data["queries"]) > 0:
                entry = self.shared_data["queries"].pop(0) 
                self.execute_query(entry)
            else:
                time.sleep(0.2)

    def execute_query(self, entry):
        self.db_manager.execute_query(entry)
        
    def wait_for_queries(self):
        while len(self.shared_data["queries"]) > 0:
            time.sleep(0.2)