
"""
This script runs through (models) and gets a recommendation (i.e. manually water today or don't manually water today)

It stores this recommendation in the database (so we can assess actual performance in due course) 
along with the model name (so we can have multiple models running simultaneously and compare their performance)

It sends emails if the model recommends that we manually water (based on one or more models)

This script will move into the daily_run.py script (or be called by it) once it's developed
"""

from datetime import datetime
import smtplib, ssl
import subprocess
import time

# Logging setup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import database, prepare_data, pred_models

MODELS=['logic']

def daily_pred():
    """
    Get a prediction for whether or not to manually water today (for each model in MODELS list)

    Call process_pred function to save the prediction data in the database (for models to use to avoid watering unnecessarily in the future)
    and send an email if a positive prediction was made
    """

    # get model(s) prediction for today
    current_date = datetime.today().date().strftime('%Y-%m-%d')
    X = prepare_data.predictor_data_row(forecast_date=current_date)
    for model in MODELS:
        if model == 'logic':
            pred = pred_models.logic(X=X)
            pred_text = "1 (manually water today)" if pred == 1 else "0 (don't manually water today)"
            logger.debug(f"model {model} predicted {pred_text}")
        process_pred(current_date, model, pred)

def process_pred(current_date: str, model: str, pred: int):
    """
    Process a model prediction, adding the prediction made to the database and sending an email if manual watering is required.

    Args:
        current_date (str): today's date in yyyy-mm-dd format
        model (str): A unique name for the model making the prediction
        pred (int): 1 to manually water today, 0 to not manually water today
    """

    db = database.RainfallDatabase()
    db.add_preds_data(model=model, date=current_date, pred=pred)
    logger.info(f"Added {model} model prediction of {pred} for {current_date} to the database.")

    if pred: # note in Python 0 is falsy and 1 is truthy (along with all other non zero values)
        send_email(model)
        logger.debug(f"Model {model} predicted we should manually water, need to send an email")
    
def send_email(model=""):

    # placeholder based on https://realpython.com/python-send-email/

    try:

        # Start the local SMTP Debugging Server
        process = subprocess.Popen(['python', '-m', 'smtpd', '-c', 'DebuggingServer', '-n', 'localhost:1025'])

        # Give the server a moment to start
        time.sleep(2)

        # Your email parameters (for testing with local server)
        sender_email = "my@gmail.com"
        receiver_email = "your@gmail.com"
        password = "your_password_here"  # for local testing, you can skip input
        message = f"""\
        Subject: Time to water your plants!

        The {model} model thinks you should water your plants today. Have a great day!"""

        # Set up the server to connect to your local SMTP DebuggingServer
        smtp_server = "localhost"
        port = 1025  # Adjusted for local server
        context = ssl.create_default_context()

        # Send the email using the local server
        with smtplib.SMTP(smtp_server, port) as server:
            server.set_debuglevel(1)  # Enables debugging output
            server.sendmail(sender_email, receiver_email, message)

    finally:
        # Stop the server
        process.terminate()

if __name__ == "__main__":

    if True: # standard operation - run through each model, make a prediction, save data to database and send watering emails
        daily_pred()