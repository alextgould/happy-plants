
"""
This script receives a recommendation from a model (i.e. manually water today or don't manually water today)

It stores this recommendation in the database (so we can assess actual performance in due course) 
along with the model name (so we can have multiple models running simultaneously and compare their performance)

It also sends emails if the model recommends that we manually water (based on one or more models)
"""

from datetime import datetime
import smtplib, ssl
import subprocess
import time

# Logging setup
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import database

def process_pred(model: str, pred: int):
    """
    Processes a model prediction, adding the prediction data to the database
    and sending an email if manual watering is required.

    Args:
        model (str): A unique name for the model making the prediction
        pred (int): 1 to manually water today, 0 to not manually water today
    """

    db = database.RainfallDatabase()

    current_date = datetime.today().date().strftime('%Y-%m-%d')
    db.add_preds_data(model=model, date=current_date, pred=pred)

    if pred:
        #send_email()
        logger.debug(f"Model {model} predicted we should manually water, need to send an email")
    else:
        logger.debug(f"Model {model} predicted no need to water, so no need to send an email")

def send_email():

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
        message = """\
        Subject: Hi there

        This message is sent from Python."""

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

# PLACEHOLDER CODE (ChatGPT)

if False:

    from src.database import get_historical_data
    from src.rl_model import train_model, predict_watering

    def main():
        df = get_historical_data()
        model = train_model(df)
        should_water = predict_watering(model, df.tail(1))
        
        if should_water:
            print("Time to water your plants!")

if __name__ == "__main__":

    if True: # for testing
        db = database.RainfallDatabase()
        db.create_preds_table()
        process_pred("test model 1", 1)
        process_pred("test model 2", 0)
        preds = db.get_preds_data()
        logger.debug(f"\npreds table:\n{preds}")

    if False: # for testing
        send_email()