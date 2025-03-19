
# PLACEHOLDER CODE (ChatGPT)
# can run in the background i.e. python src/automation.py &
# will likely go with a different approach

if False:

    import schedule
    import time
    import subprocess

    def run_data_collection():
        subprocess.run(["python", "scripts/collect_data.py"])

    def run_model_training():
        subprocess.run(["python", "scripts/train_model.py"])

    def run_notifications():
        subprocess.run(["python", "scripts/notify.py"])

    schedule.every().day.at("07:00").do(run_data_collection)
    schedule.every().sunday.at("08:00").do(run_model_training)
    schedule.every().day.at("09:00").do(run_notifications)

    while True:
        schedule.run_pending()
        time.sleep(60)
