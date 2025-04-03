"""
This script extracts relevant data from the database and prepares it for modelling

The forecast data in the database looks like this:

index         date_forecast_was_made    date_forecast_applies_to  rain_chance  rain_mm_low  rain_mm_high
0             2025-03-20                2025-03-20                0.1          0.0           0.0
1             2025-03-20                2025-03-21                0.5          0.0           3.0
2             2025-03-20                2025-03-22                0.4          0.0           1.0

The historical data in the database looks like this:

index   date                rainfall_mm
75      2025-03-17          4.0
76      2025-03-18          0.0
77      2025-03-19          3.0
78      2025-03-20          0.0

The preds data in the database looks like this:

index   model         date          pred
0       test model 1  2025-03-20    1
1       test model 2  2025-03-20    0

Our modelling data needs to have one record for each point at which the algorithm is making a prediction. For example:
date        hist_1  hist_2  hist_3  ...     chance_1    chance_2    ...     mm_1    mm_2    ...
2025-03-20  3.0     0.0     4.0     ...     0.5         0.4         ...     3.0     1.0     ...

At this early stage it seems the rain_mm_low is ALWAYS 0.0 so let's ignore this and just use rain_mm_high.

We also want to replace the hist values where the (current) model predicted watering was required with an assumed manual watering amount.

This single row of data will be sent to the model(s) to provide a recommendation (inference).

We can also use this function to create batches of training data, by taking the data at historical points 
and also extracting the actual historical rain for that day.

"""

# Logging setup
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import pandas as pd
import database

# amount of water assumed to be administered in response to a historical notification that the user should water their plants
DEFAULT_WATER_MM=20

def predictor_data_row(forecast_date='', forecast_model='', hist_days=7, forecast_days=7, include_current_day_forecast=True):
    """
    Create a single line of predictor data using historical data and forecast data from the database

    Args:
        forecast_date (str): the date the forecast is made in ISO 8601 format e.g. '2025-03-20'
        forecast_model (str): used to pick up historical positive water predictions, replacing historical data with DEFAULT_WATER_MM
        hist_days (int): the number of historical days (before the current day) to include (Default: 7)
        forecast_days (int): the number of future days (after the current day) to include (Default: 7)
        include_current_day_forecast (boolean): include yestereday's forecast for today's rain chance and mm (Default: True)

    Returns:
        df (DataFrame): contains a single row for the forecast date with columns of the relevant historical and forecast data
    """

    if forecast_date == "":
        forecast_date = datetime.today().date().strftime('%Y-%m-%d') # e.g. '2025-03-21'
    forecast_dt = datetime.strptime(forecast_date, '%Y-%m-%d')

    db = database.RainfallDatabase()

    # get date cut offs for the historical data and/or forecast data in ISO 8601 format

    start_dt = forecast_dt - timedelta(days=hist_days)
    start_date = start_dt.strftime('%Y-%m-%d')
    end_dt = forecast_dt + timedelta(days=forecast_days)
    end_date = end_dt.strftime('%Y-%m-%d')
    prior_dt = forecast_dt - timedelta(days=1)
    prior_day = prior_dt.strftime('%Y-%m-%d')

    # filter relevant data

    db_forecast_filter = f"date_forecast_was_made='{forecast_date}' AND date_forecast_applies_to > '{forecast_date}' AND date_forecast_applies_to <= '{end_date}'"
    df_forecast = db.get_forecast_data(filter=db_forecast_filter)
    
    db_historical_filter = f"date >= '{start_date}' AND date < '{forecast_date}'"
    df_historical = db.get_historical_data(filter=db_historical_filter)
    
    db_preds_filter = db_historical_filter + f" AND model = '{forecast_model}' AND pred = 1"
    df_preds = db.get_preds_data(filter=db_preds_filter)

    if include_current_day_forecast:
        db_current_day_forecast_filter = f"date_forecast_was_made='{prior_day}' AND date_forecast_applies_to = '{forecast_date}'"
        df_current_day_forecast = db.get_forecast_data(filter=db_current_day_forecast_filter)

    # add indices based on date differences
    df_historical['hist_index'] = (forecast_dt - df_historical['date']).dt.days
    df_forecast['forecast_index'] = (df_forecast['date_forecast_applies_to'] - forecast_dt).dt.days
    
    # where the model recommended watering, assume this was done at the default_water_mm
    df_historical.loc[df_historical['date'].isin(df_preds['date']), 'rainfall_mm'] = DEFAULT_WATER_MM

    # pivot data into columns in dict
    hist_mm = {f'hist_{row.hist_index}': row.rainfall_mm for _, row in df_historical.iterrows()}
    forecast_chance = {f'chance_{row.forecast_index}': row.rain_chance for _, row in df_forecast.iterrows()}
    forecast_mm = {f'mm_{row.forecast_index}': row.rain_mm_high for _, row in df_forecast.iterrows()}
    
    # add current day forecast
    if not df_current_day_forecast.empty:
        forecast_chance['chance_0'] = float(df_current_day_forecast.iloc[0]['rain_chance'])
        forecast_mm['mm_0'] = float(df_current_day_forecast.iloc[0]['rain_mm_high'])
    
    # merge all data
    model_data = {'date': forecast_date, **hist_mm, **forecast_chance, **forecast_mm}
    col_order = ['date'] + sorted(hist_mm.keys()) + sorted(forecast_chance.keys()) + sorted(forecast_mm.keys())
    df = pd.DataFrame([model_data], columns=col_order)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    logger.debug(f"predictor_data_row: {df}")
    return df

def create_X_train(forecast_model=''):
    """
    Create DataFrame with predictor variables to use for training the model by concatenating the results of multiple calls
    to the predictor_data_row function, doing so once for each forecast value in the database.

    Args:
        forecast_model (str): used to pick up historical positive water predictions, replacing historical data with DEFAULT_WATER_MM
    """

    db = database.RainfallDatabase()
    df_forecast = db.get_forecast_data()
    X_train = pd.DataFrame()
    for forecast_date in df_forecast["date_forecast_was_made"].unique():
        data_row = predictor_data_row(forecast_date=forecast_date.strftime('%Y-%m-%d'), forecast_model=forecast_model)
        X_train = pd.concat([X_train, data_row], ignore_index=True)
    logger.debug(f"created X_train: {X_train}")
    return X_train

def create_y_train(X_train, forecast_model=''):
    """
    Create training target dataframe by looking up the historical actual values for a corresponding training predictor dataframe.

    Args:
        X_train (DataFrame): contains date column to determine the target values for
        forecast_model (str): used to pick up historical positive water predictions, replacing historical data with DEFAULT_WATER_MM

    Returns:
        y_train (DataFrame): one row for each forecast date in df_pred, containing target (int) indicating whether manual watering
            should have been done (1) or not (0)
    """

    # using all historical data as the scope of the project is small, otherwise would filter it
    db = database.RainfallDatabase()
    df_historical = db.get_historical_data()
    
    # replace historical data on dates where this model indicated we should manually water
    db_preds_filter = f"model = '{forecast_model}' AND pred = 1"
    df_preds = db.get_preds_data(filter=db_preds_filter)    
    df_historical.loc[df_historical['date'].isin(df_preds['date']), 'rainfall_mm'] = DEFAULT_WATER_MM

    # aggregate up the 7 days to each date
    df_historical["rainfall_mm_week"] = df_historical["rainfall_mm"].rolling(window=7, min_periods=7).sum()
    logger.debug(f'df_historical with 7 day aggregate: {df_historical}')

    # merge aggregate values and calculate the target variable: model should output 1 (manual water) if rainfall_mm_week
    # including any adjustments for actual watering at default value, is less than target value, and 0 otherwise
    y_train = pd.merge(X_train, df_historical, on='date', how='left')
    y_train["target"] = (y_train["rainfall_mm_week"] < DEFAULT_WATER_MM).astype(int)
    y_train = y_train[['date', 'target']]
    logger.debug(f"created y_train: {y_train}")
    return y_train

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # test single line of predictor data
    if True:
        X_train = predictor_data_row(forecast_date='2025-04-03', forecast_model='logic')
        #y_train = create_y_train(X_train)

    # test multiple lines of predictor data and corresponding targets
    #forecast_model = "test model 1"
    #X_train = create_X_train()
    #y_train = create_y_train(X_train)