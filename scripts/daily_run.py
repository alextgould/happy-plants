
"""
This script is designed to be run on a daily basis using Windows Task Scheduler or Linux cron/systemd

It sources the forecast data and the historical data from the web scraping tool and places the data into the database.
It then runs the predictions for each model in MODELS and sends an email with the latest rain forecasts as an image
along with the model predictions.
"""

# Logging setup (specifying file here means you don't need to redirect log outputs when setting up Task Scheduler etc)
import logging
import os
log_file = os.path.join(os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.log") # e.g. collect_data.py -> collect_data.log
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.debug(f"log_file being written to {log_file}")
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

# Add src to path (rather than having to create .vscode\settings.json, adjust PYTHONPATH in Task Scheduler etc)
import sys
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if src_path not in sys.path:
    sys.path.append(src_path)
    logger.debug(f"appending {src_path} to sys.path so that modules in src directory can be imported")

# Standard imports
from datetime import datetime

# Local imports
from get_data import forecast_data, historical_data
import database, prepare_data, pred_models, send_email, create_plots

# Global parameters
MODELS=['logic']

def get_data():
    """Get the new historical and forecast data and place it in the database."""

    # get new data using the web scraper
    df_forecast = forecast_data()
    df_historical = historical_data()
    logger.info(f"New forecast data: {df_forecast}")
    logger.info(f"New historical data: {df_historical}")

    # save the data to the database    
    db = database.RainfallDatabase()
    db.add_forecast_data(df_forecast)
    db.add_historical_data(df_historical)


def daily_pred(models=MODELS):
    """
    Generate predictions for whether or not to manually water today, for each model in the provided list.

    Args:
        models (list, optional): A list of models to generate predictions for. Defaults to the global 'MODELS' variable.

    Returns:
        list: A list of tuples, each containing a model name (str) and its prediction (int).
            The prediction value indicates whether manual watering is needed today.
    """

    current_date = datetime.today().date().strftime('%Y-%m-%d')
    X = prepare_data.predictor_data_row(forecast_date=current_date)
    preds = []
    for model in models:
        if model == 'logic':
            pred = pred_models.logic(X=X)
            pred_text = "1 (manually water today)" if pred == 1 else "0 (don't manually water today)"
            logger.debug(f"model {model} predicted {pred_text}")
        else:
            raise ValueError(f"Model must be one of {MODELS}")
        add_pred_data(current_date, model, pred) # add to the database
        preds.append([model, pred]) # add to the return list
    return preds

def add_pred_data(current_date: str, model: str, pred: int):
    """
    Process a model prediction, adding the prediction made to the database 

    Args:
        current_date (str): today's date in yyyy-mm-dd format
        model (str): A unique name for the model making the prediction
        pred (int): 1 to manually water today, 0 to not manually water today
    """

    db = database.RainfallDatabase()
    db.add_preds_data(model=model, date=current_date, pred=pred)
    logger.info(f"Added {model} model prediction of {pred} for {current_date} to the database.")

if __name__ == "__main__":

    # get new data and place it in the database
    get_data()

    # make new model predictions
    preds = daily_pred()
    
    # update the forecast chart so we can attach it to the daily email
    import create_plots
    image_path = create_plots.plot_forecast(file_name="forecast.png")

    # create email body, including predictions from models
    body = "Here is the historical and forecast rainfall data for today:\n\n<img>"
    for model_pred in preds:
        model, pred = model_pred
        pred_text = "1 (manually water today)" if pred == 1 else "0 (don't manually water today)"
        body += f"\n\nBased on the data, {model} predicted {pred_text}."

    # send email
    send_email.send_email(subject="Daily rainfall data and watering advice", body=body, attach_path=image_path)