
# placeholder based on https://realpython.com/python-send-email/

import smtplib, ssl
import subprocess
import time

def test_email():

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
    test_email()