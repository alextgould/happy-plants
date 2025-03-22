
"""
This script is designed to be run on a daily basis using Windows Task Scheduler or Linux cron/systemd

It sources both the forecast data and the historical data from the web scraping tool
and places the data into the database.

You can also import specific modules from this script file
"""

# Logging setup (specifying file here means you don't need to redirect log outputs when setting up Task Scheduler etc)
import logging
import os
log_file = os.path.join(os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.log") # e.g. collect_data.py -> collect_data.log
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
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

    # get new data using the web scraper
    df_forecast = forecast_data()
    df_historical = historical_data()
    logger.info(f"New forecast data: {df_forecast}")
    logger.info(f"New historical data: {df_historical}")

    # save the data to the database    
    db = database.RainfallDatabase()
    db.add_forecast_data(df_forecast)
    db.add_historical_data(df_historical)

if __name__ == "__main__":
    main()