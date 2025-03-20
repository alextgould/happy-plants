
"""
This script sources both the forecast data and the historical data from the web scraping tool
and places the data into the database. Ideally this gets run once daily by task schedular / cron / systemd
"""

# Logging setup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from get_data import forecast_data, historical_data
import database

def main():

    db = database.RainfallDatabase()

    df_forecast = forecast_data()
    db.add_forecast_data(df_forecast)
    
    df_historical = historical_data()
    db.add_historical_data(df_historical)

    logger.debug(f"New forecast data: {df_forecast}")
    logger.debug(f"New historical data: {df_historical}")
    df_forecast = db.get_forecast_data()
    df_historical = db.get_historical_data()
    logger.debug(f"Forecast data now in the database: {df_forecast}")
    logger.debug(f"Historical data now in the database: {df_historical}")

if __name__ == "__main__":
    main()