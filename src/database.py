"""
This script defines a RainfallDatabase class that can create or reset the database tables, add data to the database,
and extract data from the database, handling formatting (mainly dates) and input/output data types (mainly python dataframes).

Example usage:

    db = database.RainfallDatabase()
    df_tables = db.check_tables()
    df_forecast = db.get_forecast_data()
    df_historical = db.get_historical_data()
    df_preds = db.get_preds_data()
"""

import os
import sqlite3
import pandas as pd

# Logging setup
import logging
logger = logging.getLogger(__name__)

# Dynamically determine the database location based on this file's location
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "data", "rainfall.db")

class RainfallDatabase:
    def __init__(self, db_path=DEFAULT_DB_PATH):
        """Initialize database with a given path."""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file does not exist at {self.db_path}")

    def _connect(self):
        """Helper function to create a database connection."""
        return sqlite3.connect(self.db_path)
    
    # Functions to create (or reset) database tables

    def create_forecast_table(self, reset=False):
        """Create the forecast table, with an option to reset it."""
        with self._connect() as conn:
            cur = conn.cursor()
            if reset:
                logger.info("Resetting forecast table")
                cur.execute("DROP TABLE IF EXISTS forecast;")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS forecast (
                date_forecast_was_made TEXT,
                date_forecast_applies_to TEXT,
                rain_chance REAL,
                rain_mm_low REAL,
                rain_mm_high REAL,
                PRIMARY KEY (date_forecast_was_made, date_forecast_applies_to)
            );
            """)
            conn.commit()
            logger.info("Forecast table created or verified successfully.")

    def create_historical_table(self, reset=False):
        """Create the historical table, with an option to reset it."""
        with self._connect() as conn:
            cur = conn.cursor()
            if reset:
                logger.info("Resetting historical table")
                cur.execute("DROP TABLE IF EXISTS historical;")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS historical (
                date TEXT PRIMARY KEY,
                rainfall_mm REAL
            );
            """)
            conn.commit()
            logger.info("Historical table created or verified successfully.")

    def create_preds_table(self, reset=False):
        """
        Create the model predictions (preds) table, with an option to reset it.
        """
        with self._connect() as conn:
            cur = conn.cursor()
            if reset:
                logger.info("Resetting preds table")
                cur.execute("DROP TABLE IF EXISTS preds;")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS preds (
                model TEXT,
                date TEXT,
                pred INTEGER,  -- 0 for FALSE (don't manually water today), 1 for TRUE (do manually water today)
                PRIMARY KEY (model, date)
            );
            """)
            conn.commit()
            logger.info("Preds table created or verified successfully.")

    def check_tables(self):
        """Print the schema of all tables in the sqlite database."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            if not tables:
                logger.WARNING("No tables found in the database.")
                return

            schema_data = []
            for table in tables:
                table_name = table[0]
                cur.execute(f"PRAGMA table_info({table_name});")
                columns = cur.fetchall()
                for col in columns:
                    schema_data.append((table_name, *col))

            df_schema = pd.DataFrame(schema_data, columns=["Table Name", "Column Index", "Column Name", "Data Type", "Allows NULL", "Default Value", "Primary Key"])
            return df_schema
        
    # Forecast data

    def add_forecast_data(self, df_to_add):
        """Add forecast data to the database."""
        with self._connect() as conn:
            cur = conn.cursor()
            for _, row in df_to_add.iterrows():
                cur.execute("""
                INSERT OR REPLACE INTO forecast (
                    date_forecast_was_made, date_forecast_applies_to, rain_chance, rain_mm_low, rain_mm_high
                ) VALUES (?, ?, ?, ?, ?)
                """, (row['date_forecast_was_made'].strftime('%Y-%m-%d'),
                      row['date_forecast_applies_to'].strftime('%Y-%m-%d'),
                      row['rain_chance'], row['rain_mm_low'], row['rain_mm_high']))
            conn.commit()

    def get_forecast_data(self, filter: str = "") -> pd.DataFrame:
        """
        Retrieve forecast data from the database with an optional filter.

        Args:
            filter (str, optional): An SQL WHERE condition to filter the results.
                Example: filter="date_forecast_applies_to='2025-03-25'". If no filter
                is provided, all forecast data is returned.

        Returns:
            pandas.DataFrame: A DataFrame containing the forecast data, with the
            'date_forecast_was_made' and 'date_forecast_applies_to' columns
            converted to datetime format.
        """
        with self._connect() as conn:
            query = "SELECT * FROM forecast"
            if filter:
                query += f" WHERE {filter}"
            df = pd.read_sql(query, conn)
            df['date_forecast_was_made'] = pd.to_datetime(df['date_forecast_was_made'], format='%Y-%m-%d')
            df['date_forecast_applies_to'] = pd.to_datetime(df['date_forecast_applies_to'], format='%Y-%m-%d')
            return df
        
    # Historical data

    def add_historical_data(self, df_to_add):
        """Add historical data to the database."""
        with self._connect() as conn:
            cur = conn.cursor()
            for _, row in df_to_add.iterrows():
                cur.execute("""
                INSERT OR REPLACE INTO historical (date, rainfall_mm)
                VALUES (?, ?)
                """, (row['date'].strftime('%Y-%m-%d'), str(row['rainfall_mm'])))
            conn.commit()

    def get_historical_data(self, filter: str = "") -> pd.DataFrame:
        """
        Retrieve historical data from the database with an optional filter.

        Args:
            filter (str, optional): An SQL WHERE condition to filter the results.
                Example: filter="date_forecast_was_made='2025-03-25'". If no filter
                is provided, all historical data is returned.

        Returns:
            pandas.DataFrame: A DataFrame containing the historical data, with the
            'date' column converted to datetime format.
        """
        with self._connect() as conn:
            query = "SELECT * FROM historical"
            if filter:
                query += f" WHERE {filter}"
            df = pd.read_sql(query, conn)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            return df
        
    # Predictions data

    def add_preds_data(self, model: str, date: str, pred: int):
        """Add preds data to the database."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO preds (model, date, pred)
                VALUES (?, ?, ?)
                """, (model, date, pred))
            conn.commit()

    def get_preds_data(self, filter: str = "") -> pd.DataFrame:
        """
        Retrieve predictions data from the database with an optional filter.

        Args:
            filter (str, optional): An SQL WHERE condition to filter the results.
                Example: filter="date='2025-03-25'". If no filter is provided,
                all predictions data is returned.

        Returns:
            pandas.DataFrame: A DataFrame containing the predictions data, with the
            'date' column converted to datetime format.
        """
        with self._connect() as conn:
            query = "SELECT * FROM preds"
            if filter:
                query += f" WHERE {filter}"
            df = pd.read_sql(query, conn)
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            return df
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = RainfallDatabase()
    df_tables = db.check_tables()
    logger.debug(f"\nTables in the database:\n{df_tables}")
    df_forecast = db.get_forecast_data()
    logger.debug(f"\nForecast data in the database:\n{df_forecast}")
    df_historical = db.get_historical_data()
    logger.debug(f"\nHistorical data in the database:\n{df_historical}")
    df_preds = db.get_preds_data()
    logger.debug(f"\nPreds data in the database:\n{df_preds}")