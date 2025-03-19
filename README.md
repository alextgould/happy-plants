
# Happy Plants: A data-driven predictive watering notification system

![](img/robots.png)

This project is currently under development

## Project aim

The goal of this project is to build a system that will notify me when it's a good time to manually water my plants.

In order to this, we will:

* use APIs and web scraping tools to gather historical and forecast rainfall data for my local area (Sydney)

* save the data into an sqlite database

* train a reinforcement learning model to predict when is the best time to manually water the plants

* use automation tools to ensure the data is gathered automatically on a daily basis and the model constantly improved as more data is obtained

We may also

* bootstrap the process with some synthetic data (noting that there isn't a history of forecasts, only of actual rainfall)

* host the system on AWS or GCP

* use terraform to create a reproducable infrastructure model that others can use to deploy the system

## Repo structure

Draft structure of the repo below (subject to change e.g. may not do automation using Python). Note not all of the files have been developed yet. Notebooks are a useful way of developing the code and will be referenced in a blog post, but aren't used directly in the end product.

```bash
happy-plants/
│── data/                  # while storing data locally (not committed)
│── notebooks/             # Jupyter notebooks for prototyping
│── src/                   # Main Python code
│   │── __init__.py        # Marks src as a package
│   │── data_ingestion.py  # Scraping/APIs for rainfall data
│   │── database.py        # Handles SQLite interactions
│   │── rl_model.py        # Defines & trains the RL model
│   │── automation.py      # Scheduling & automation logic
│── scripts/               # Executable scripts for automation
│   │── collect_data.py    # Runs data collection pipeline
│   │── train_model.py     # Trains the model
│   │── notify.py          # Sends watering notifications
│── terraform/             # Infrastructure-as-code for cloud deployment
│── requirements.txt       # Python dependencies
│── .env                   # Environment variables (gitignored)
│── README.md              # Project documentation
│── .gitignore             # Ignore unnecessary files
```