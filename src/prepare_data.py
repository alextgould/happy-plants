"""
This script extracts relevant data from the database and prepares it for modelling

The forecast data in the database looks like this:

date_forecast_was_made date_forecast_applies_to  rain_chance  rain_mm_low  rain_mm_high
0             2025-03-20               2025-03-20          0.1          0.0           0.0
1             2025-03-20               2025-03-21          0.5          0.0           3.0
2             2025-03-20               2025-03-22          0.4          0.0           1.0
3             2025-03-20               2025-03-23          0.5          0.0           3.0
4             2025-03-20               2025-03-24          0.4          0.0           1.0
5             2025-03-20               2025-03-25          0.4          0.0           3.0
6             2025-03-20               2025-03-26          0.5          0.0           5.0

The historical data in the database looks like this:

date  rainfall_mm
0  2025-01-01          0.0
1  2025-01-02          0.0
2  2025-01-03          4.8
3  2025-01-04          0.2
4  2025-01-05          0.0
..        ...          ...
74 2025-03-16          0.0
75 2025-03-17          4.0
76 2025-03-18          0.0
77 2025-03-19          3.0
78 2025-03-20          0.0

Our modelling data needs to have one record for each point at which the algorithm is making a prediction. For example:
date    hist_1 hist_2 hist_3 hist_4 ... chance_1    chance_2    chance_3 ...    mm_low_1 mm_low_2 mm_low_3  ... mm_high_1 mm_high_2 mm_high_3 ...
2025-03-20  3.0 0.0 4.0 0.0 ... 0.5 0.4 0.5 ... 0.0 0.0 0.0 ... 3.0 1.0 3.0

General approach is to pick up the historical days leading up to the forecast day,
along with all forecast_applies_to data for the date_forecast_was_made day,
Flatten both of these, using the difference between the date and the forecast date to produce an index
Then keep the relevant ones (e.g. past X days, next Y days)
Also consider "feature selection" e.g. if the success criteria is 20mm per week, add up the watering for the past 6 days
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
"""

import logging
logging.basicConfig(level=logging.DEBUG)

from datetime import datetime, timedelta

from database import get_forecast_data, get_historical_data

def create_model_data(forecast_date='2025-03-20'):
    """Create a single line of data using historical data and forecast data from the database"""

    df_forecast = get_forecast_data() # check it works with no filter
    logging.debug(f"Forecast data: {df_forecast}")

    df_historical = get_historical_data() # check it works with no filter
    logging.debug(f"Historical data: {df_historical}")
    
    forecast_date_obj = datetime.strptime(forecast_date, '%Y-%m-%d')
    historical_start_date = forecast_date_obj - timedelta(days=6)
    historical_start_date_str = historical_start_date.strftime('%Y-%m-%d')
    logging.debug(f"forecast_date_obj: {forecast_date_obj} historical_start_date: {historical_start_date} historical_start_date_str: {historical_start_date_str}")

    df_forecast = get_forecast_data(filter=f"date_forecast_was_made={forecast_date}")
    df_historical = get_historical_data(filter=f"date >= {historical_start_date_str} AND date <= {forecast_date}")
    logging.debug(f"Forecast data: {df_forecast}")
    logging.debug(f"Historical data: {df_historical}")

if __name__ == "__main__":
    create_model_data()