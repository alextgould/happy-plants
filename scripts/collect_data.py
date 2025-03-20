
"""
This script sources both the forecast data and the historical data from the web scraping tool
and places the data into the database. Ideally this gets run once daily by task schedular / cron / systemd
"""

# Logging setup (specifying file here means you don't need to redirect log outputs when setting up Task Scheduler etc)
import logging
import os
log_file = os.path.join(os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.log") # e.g. collect_data.py -> collect_data.log
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.debug(f"log_file being written to {log_file}")

# Add src to path (rather than having to create .vscode\settings.json, adjust PYTHONPATH in Task Scheduler etc)
import sys
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_path not in sys.path:
    sys.path.append(src_path)
    logger.info(f"appending {src_path} to sys.path so that modules in src directory can be imported")

# Local imports
from get_data import forecast_data, historical_data
import database

# Main code
def main():

    db = database.RainfallDatabase()

    df_forecast = forecast_data()
    db.add_forecast_data(df_forecast)
    
    df_historical = historical_data()
    db.add_historical_data(df_historical)

    logger.info(f"New forecast data: {df_forecast}")
    logger.info(f"New historical data: {df_historical}")
    df_forecast = db.get_forecast_data()
    df_historical = db.get_historical_data()
    # note that leaving logger set to debug level will clog the log as it prints the full database every time
    logger.debug(f"Forecast data now in the database: {df_forecast}")
    logger.debug(f"Historical data now in the database: {df_historical}")

if __name__ == "__main__":
    main()