
# Logging
import logging
logger = logging.getLogger(__name__)

# Python standard
import os
import sqlite3

# Third-party
import pandas as pd

# Dynamically determine the database location based on this file's location
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "data", "rainfall.db")

def resolve_db_path(db_path):
    """Used in most functions to pick up the default path and confirm path exists"""

    # Resolve the full path of the database
    if db_path == "":
        db_path = DEFAULT_DB_PATH

    # Check database exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file does not exist at {db_path}")
    
    return db_path

# Create tables

def create_forecast_table(db_path="", reset=False):
    """
    Create the forecast table.

    Keyword arguments:
    db_path (str): Path to the SQLite database file. Defaults to "../data/rainfall.db".
    reset (bool): If True, drops and recreates the table. Defaults to False.
    """

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        if reset:
            logging.info("Resetting forecast table")
            cur.execute("DROP TABLE IF EXISTS forecast;")

        # Create table if it doesn't already exist
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
        logging.info("Forecast table created or verified successfully.")

def create_historical_table(db_path="", reset=False):
    """
    Create the historical table.

    Keyword arguments:
    db_path (str): Path to the SQLite database file. Defaults to "../data/rainfall.db".
    reset (bool): If True, drops and recreates the table. Defaults to False.
    """

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        if reset:
            logging.info("Resetting historical table")
            cur.execute("DROP TABLE IF EXISTS historical;")

        # Create table if it doesn't already exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS historical (
            date TEXT PRIMARY KEY,
            rainfall_mm REAL
        );
        """)
        conn.commit()
        logging.info("Forecast table created or verified successfully.")

def check_tables(db_path=""):
    """Print the schema of all tables in the SQLite database at db_path"""

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()

        if not tables:
            print("No tables found in the database.")
            return
        
        schema_data = []

        for table in tables:
            table_name = table[0]
            cur.execute(f"PRAGMA table_info({table_name});")
            columns = cur.fetchall()

            for col in columns:
                schema_data.append((table_name, *col))

        df_schema = pd.DataFrame(schema_data, columns=["Table Name", "Column Index", "Column Name", "Data Type", "Allows NULL", "Default Value", "Primary Key"])
        print(df_schema)

# Forecast data

def add_forecast_data(df_to_add, db_path=""):
    """Add data from df_to_add into the forecast table in the sqlite database at db_path"""

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Add data from the dataframe to the database, ensuring idempotent (no duplicates, latest values are retained)
        for _, row in df_to_add.iterrows():
            cur.execute("""
            INSERT OR REPLACE INTO forecast (
                date_forecast_was_made, date_forecast_applies_to, rain_chance, rain_mm_low, rain_mm_high
            ) VALUES (?, ?, ?, ?, ?)
            """, (row['date_forecast_was_made'].strftime('%Y-%m-%d'), row['date_forecast_applies_to'].strftime('%Y-%m-%d'), row['rain_chance'], row['rain_mm_low'], row['rain_mm_high']))
        conn.commit()

def get_forecast_data(db_path="", filter=""):

    db_path = resolve_db_path(db_path)
    """
    Retrieve data from the forecast table in the sqlite database at db_path, using SELECT * FROM forecast.

    The forecast database has primary key fields `date_forecast_was_made` and `date_forecast_applies_to`
    and values in `rain_chance`, `rain_mm_low`, `rain_mm_high`.

    Args:
        filter (str): Optional. A WHERE condition to append to the SELECT query.
            Example:
                filter="date_forecast_was_made = '2025-03-19'"  
                # Retrieves records for March 19, 2025.
            Example:
                filter="date_forecast_was_made > '2025-03-19'"  
                # Retrieves records for dates after March 19, 2025.

    Returns:
        pandas.DataFrame: A dataframe with dates formatted as pandas datetime.
    """

    with sqlite3.connect(db_path) as conn:
        query = "SELECT * FROM forecast"
        if filter:
            query += f" WHERE {filter}"
        df = pd.read_sql(query, conn)

        # convert dates
        df['date_forecast_was_made'] = pd.to_datetime(df['date_forecast_was_made'])
        df['date_forecast_applies_to'] = pd.to_datetime(df['date_forecast_applies_to'])
        return df
    
# Historical data

def add_historical_data(df_to_add, db_path=""):
    """Add data from df_to_add into the historical table in the sqlite database at db_path"""

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        # Add data from the dataframe to the database, ensuring idempotent (no duplicates, latest values are retained)
        for _, row in df_to_add.iterrows():
            cur.execute("""
            INSERT OR REPLACE INTO historical (
                date, rainfall_mm
            ) VALUES (?, ?)
            """, (str(row['date']), str(row['rainfall_mm'])))
        conn.commit()

def get_historical_data(db_path="", filter=""):
    """Retrieve data from the historical table in the sqlite database at db_path, using SELECT * FROM historical.

    The historical database has primary key field date and values in rainfall_mm.

        Args:
        filter (str): Optional. A WHERE condition to append to the SELECT query.
            Example:
                filter="date = '2025-03-19'"  
                # Retrieves records for March 19, 2025.
            Example:
                filter="date > '2025-03-19'"  
                # Retrieves records for dates after March 19, 2025.

    Returns:
        pandas.DataFrame: A dataframe with dates formatted as pandas datetime.
    """

    db_path = resolve_db_path(db_path)

    with sqlite3.connect(db_path) as conn:
        query = "SELECT * FROM historical"
        if filter:
            query += f" WHERE {filter}"
        df = pd.read_sql(query, conn)

        # convert dates
        df['date'] = pd.to_datetime(df['date'])
        return df