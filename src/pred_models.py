"""
This script contains predictive model(s) that take the data created in prepare_data.py
and return a prediction (1 = manually water today, 0 = don't water today).
"""

# Logging setup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from datetime import datetime

import pandas as pd

# amount of water assumed to be administered in response to a historical notification that the user should water their plants
# should be consistent with the value in prepare_data.py
DEFAULT_WATER_MM=20

def logic(X):
    """
    A simple logic based approach: looks at the rainfall in the past six days as well as the forecast for today's rainfall
    from yesterday if the probability of rain is more than 50%, and compares this to the required watering target
    """

    # Sum past six days' rainfall
    hist_columns = [col for col in X.columns if pd.Series(col).str.contains(r'^hist_[1-6]$', regex=True).any()]
    total_rainfall = X[hist_columns].sum(axis=1).iloc[0] # use .iloc[0] to convert series to value given only one input row
    
    # Ensure mm_0 and chance_0 exist, default to 0 if missing
    mm_0 = X['mm_0'].iloc[0] if 'mm_0' in X.columns else 0
    chance_0 = X['chance_0'].iloc[0] if 'chance_0' in X.columns else 0

    # Include today's forecasted rainfall if the chance of rain is > 50%
    total_rainfall += mm_0 * (chance_0 > 0.5)

    return 1 if total_rainfall < DEFAULT_WATER_MM else 0

if __name__ == "__main__":

    # this area is for testing during development

    import prepare_data

    # get model(s) prediction for today
    current_date = datetime.today().date().strftime('%Y-%m-%d')
    X = prepare_data.predictor_data_row(forecast_date=current_date)

    pred = logic(X)
    logger.debug(f"logic model prediction: {pred}")
