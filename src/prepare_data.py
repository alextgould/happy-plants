"""
This script extracts relevant data from the database and prepares it for modelling

The forecast data in the database looks like this:

index         date_forecast_was_made    date_forecast_applies_to  rain_chance  rain_mm_low  rain_mm_high
0             2025-03-20                2025-03-20                0.1          0.0           0.0
1             2025-03-20                2025-03-21                0.5          0.0           3.0
2             2025-03-20                2025-03-22                0.4          0.0           1.0
3             2025-03-20                2025-03-23                0.5          0.0           3.0
4             2025-03-20                2025-03-24                0.4          0.0           1.0
5             2025-03-20                2025-03-25                0.4          0.0           3.0
6             2025-03-20                2025-03-26                0.5          0.0           5.0

The historical data in the database looks like this:

index   date                rainfall_mm
74      2025-03-16          0.0
75      2025-03-17          4.0
76      2025-03-18          0.0
77      2025-03-19          3.0
78      2025-03-20          0.0

The preds data in the database looks like this:

index   model         date          pred
0       test model 1  2025-03-20    1
1       test model 2  2025-03-20    0

Our modelling data needs to have one record for each point at which the algorithm is making a prediction. For example:
date    hist_1 hist_2 hist_3 hist_4 ... chance_1    chance_2    chance_3 ...    mm_low_1 mm_low_2 mm_low_3  ... mm_high_1 mm_high_2 mm_high_3 ...
2025-03-20  3.0 0.0 4.0 0.0 ... 0.5 0.4 0.5 ... 0.0 0.0 0.0 ... 3.0 1.0 3.0

We also want to replace the historical dates where the (current) model predicted watering was required with the assumed manual watering amount (TBC)

TODO - tidy this bit up and move to devlog / blog

Approach
* pick up the historical days leading up to the forecast day
* pick up all forecast_applies_to data for the date_forecast_was_made day
* Flatten both of these, using the difference between the date and the forecast date to produce an index
* Then keep the relevant ones (e.g. past X days, next Y days)
* "feature selection" e.g. if the success criteria is 20mm per week, add up the watering for the past 6 days
as this is guaranteed (and includes adjustments for assumed action taken following prior watering notifications)
and/or add up some expected rainfall (e.g. rain_chance * average of rain_mm_low and rain_mm_high, for next 1 day or possibly 
each future day. 
Relevance of this aspect might depend on what model(s) I'm using. In the short term we might go with something super simple
(e.g. just use actual past 6 days + expected for next 2 days and issue notification if <20mm), particularly while
collecting/generating data and setting up notification flow

Assumptions / Areas of uncertainty
* include current day forecast?
  - time of day that the program is run (e.g. running at the start of the day vs at the end of the day)
  - time of day that the forecasts are released (e.g. is this 9am? 6am? 12am? are they updated throughout the day? on an hourly basis?)
  - wording implies it's for the remainder of the day which could be misleading (e.g. it rains all morning, then forecast is 0.0)
  - ideal time of day to run this might depend on when the user is going to take action (e.g. free to water at 7am vs 10am vs 6pm)
* assume that past notifications resulted in watering at the required amount (need to overwrite historical data after extracting it)

Note on the forecast page
http://www.bom.gov.au/nsw/forecasts/sydney.shtml
it actually has e.g. 
"Forecast issued at 4:20 pm EDT on Thursday 20 March 2025."
so looking at this page a few times manually will probably give sufficient info to get a feeling for this
particularly if it's a day where it's been raining and clears up
"""

# Logging setup
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta

import database

def create_model_data(forecast_date='2025-03-20', hist_days=3, forecast_days=3, include_current_day_forecast=False):
    """
    Create a single line of data using historical data and forecast data from the database

    Args:
    forecast_date (str): the date the forecast is made in ISO 8601 format e.g. '2025-03-20'
    hist_days (int): the number of historical days to include
    forecast_days (int): the number of future days to include (not including the current day)
    include_current_day_forecast (boolean): whether to also include the forecast for the rest of the forecast day (Default: False)
    """

    db = database.RainfallDatabase()

    # get date cut offs for the historical data and/or forecast data in ISO 8601 format
    start_date = datetime.strptime(forecast_date, '%Y-%m-%d') - timedelta(days=hist_days-1)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.strptime(forecast_date, '%Y-%m-%d') + timedelta(days=forecast_days)
    end_date = end_date.strftime('%Y-%m-%d')
    logger.debug(f"Creating model with historical data back to {start_date} (-{hist_days} days)")
    logger.debug(f"Creating model with forecast data from {forecast_date}, for forecast days up to {end_date} (+{forecast_days} days)")
    
    # filter relevant data based on function arguments
    db_forecast_filter = f"date_forecast_was_made='{forecast_date}' AND date_forecast_applies_to <= '{end_date}'"
    if not include_current_day_forecast:
        db_forecast_filter += f" AND date_forecast_applies_to != '{forecast_date}'"
    logger.debug(f"db_forecast_filter is: {db_forecast_filter}")
    df_forecast = db.get_forecast_data(filter=db_forecast_filter)
    db_historical_filter = f"date >= '{start_date}' AND date <= '{forecast_date}'"
    logger.debug(f"db_hist_filter is: {db_historical_filter}")
    df_historical = db.get_historical_data(filter=db_historical_filter)
    df_preds = db.get_preds_data(filter=db_historical_filter + " AND pred = 1")
    
    logger.debug(f"Forecast data: {df_forecast}")
    logger.debug(f"Historical data: {df_historical}")
    logger.debug(f"Preds data: {df_preds}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    create_model_data()