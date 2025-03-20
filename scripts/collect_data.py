
import logging
logging.basicConfig(level=logging.DEBUG)

from get_data import forecast_data, historical_data
from database import add_forecast_data, add_historical_data, get_forecast_data, get_historical_data

def main():

    df_forecast = forecast_data()
    add_forecast_data(df_forecast)
    
    df_historical = historical_data()
    add_historical_data(df_historical)

    logging.debug(f"New forecast data: {df_forecast}")
    logging.debug(f"New historical data: {df_historical}")
    df_forecast = get_forecast_data()
    df_historical = get_historical_data()
    logging.debug(f"Forecast data now in the database: {df_forecast}")
    logging.debug(f"Historical data now in the database: {df_historical}")

if __name__ == "__main__":
    main()