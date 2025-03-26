
# Happy Plants: A data-driven predictive watering notification system

![](img/robots.png)

## What is the purpose of this project?

The goal of this project is to build a system that will notify me when it's a good time to manually water my plants (and gain/demonstrate some related skills along the way).

Currently, the following is in place:

* use web scraping tools to gather historical and forecast rainfall data for my local area (Sydney)

* save the data into an sqlite database

* transform the data and give it to model(s) to predict when is the best time to manually water the plants

* use automation tools to ensure the process is run automatically on a daily basis

* send emails to provide visualisations and watering recommendations

This project is still under development. Future improvements may include:

* Deploy the system to a cloud platform (GCP and/or AWS), using a Linux environment with automation using cron/systemd. This could also involve using Terraform to create a reproducable infrastructure model that others can use to deploy the system.

* Explore alternative models for making the watering recommendation, such as reinforcement learning and/or machine learning models. This could also involve creating synthetic data to train the models on (noting that there isn't a history of forecasts, only of actual rainfall).

* Create an API to register when the user waters their plants, which can be accessed by clicking a button in the daily email. This way the system doesn't have to assume that the user has watered their plants, and the user can ignore the recommendation and get a reminder the next day.

## Repo structure

The main folders and files in this repo are as follows:

```bash
happy-plants/
│── .config/               # used for credentials (not committed)
│── data/                  # contains the sqlite database (not committed)
│── notebooks/             # Jupyter notebooks for prototyping
│── img                    # Images used in this readme and when sending emails
│── scripts/               # Scripts that call modules from src folder
│   │── daily_run.py       # Runs daily pipeline
│   │── reset_database.py  # Clears all the data from the database
│── src/                   # Main Python code
│   │── create_plots.py    # Create images from data in database for emails
│   │── database.py        # Handles SQLite database interactions
│   │── get_data.py        # Source data from websites
│   │── pred_models.py     # Models that predict whether we should manually water or not
│   │── prepare_data.py    # Data manipulation for predictive models
│   │── send_email.py      # Send emails using Google's Gmail API
│── requirements.txt       # Python dependencies
│── devlog.md              # Development documentation
│── README.md              # Project documentation
│── .gitignore             # Ignore unnecessary files
```