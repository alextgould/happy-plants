# Happy Plants: A data-driven predictive watering notification system

![](img/robots.png)

## About this project

The goal of the project was to build a system that would notify me when it's a good time to manually water my plants, and gain/demonstrate some skills along the way. This includes:
* Python as the core programming language, with Jupyter notebooks used for prototyping
* Scraping data from the web using the BeautifulSoup and requests libraries
* Manipulating data using the Pandas library and storing the data in an Sqlite database
* Sending emails using the Google Gmail API, including generating and including inline data visualisations
* Daily automation using Windows Task Scheduler

You can read all about this project in its associated [blog post](https://alextgould.github.io/happy-plants/).

## Usage

If you want to try running the program yourself locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/alextgould/happy-plants.git
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Install the required dependencies (use requirements.txt if you want to use the latest versions or requirements-freeze.txt if you want to guarantee no dependency conflicts):
   ```bash
   pip install -r requirements.txt
   ```

4. To send emails, you'll need to create a Google Cloud Platform (GCP) project and configure the Gmail API. Instructions for doing this are available in the [blog post](https://alextgould.github.io/happy-plants/) and in the docstring at the top of the `src/send_email.py` file.

5. The main entry point for the program is `scripts/daily_run.py`. You can run it manually:
   ```bash
   python scripts/daily_run.py
   ```

6. To automate daily execution, you can set up `scripts/daily_run.py` using Windows Task Scheduler. Detailed instructions are available in the [blog post](https://alextgould.github.io/happy-plants/).

I'm not currently sharing the /data folder, but given it takes some time to build up a history of forecasts for modelling purposes, reach out if you would like a copy of this.

## Repo structure

The main folders and files in this repo are as follows:

```bash
happy-plants/
│── .config/               # used for credentials (not committed)
│── data/                  # contains the sqlite database (not committed)
│── notebooks/             # Jupyter notebooks for prototyping
│── img/                   # Images used in this readme and when sending emails
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