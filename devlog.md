
# About

This file is for keeping assorted notes along the way, which may be useful in later blog / documentation, retracing steps to debug or recreate similar in the future etc

# To Do

A place to park ideas for future work, to allow me to better focus on the task at hand

  - mlflow - for tracking model performance over time
  - pydantic - for structured config management
  - terraform folder
  - what happens if the BOM change their forecast page html? need a way to pick this up (python error handling and/or check data looks reasonable) and notify that things are broken (part of the automation script phase of the project)
  - more generally, go over everything with an error handling perspective (may be overkill for a project designed to demonstrate familiarity with tools such as terraform rather than python web scraping)
  - revisit the add_src_to_path.py issue, with src not being treated as a module even if __init__.py is included in it
  - consider whether to adjust code to allow for intra-day data collection in the database (with optional parameter driving this) e.g. for collecting data every 1 hour for a week in order to understand a) how often they update forecasts (both time of day and frequency within the day and whether it's regular (automated) or not (manual) b) how "rest of day" forecasts change in response to actual weather events on the forecast day (i.e. if it rains half way through the day and then clears up, will the forecast amount reduce to zero as it's already rained or will the forecast amount approach the actual amount as the day progresses)

# Historical notes

These are broadly in reverse chronological order (i.e. oldest stuff is at the bottom)

## Research - dates in databases

For database purposes, it's typically better to use %Y-%m-%d (full year) since it's the ISO 8601 standard format and more commonly recognized by most systems.

ISO 8601 defines a standardized format for representing dates, and both %Y-%m-%d and %Y/%m/%d are valid date representations, but with a slight difference in separator:

%Y-%m-%d (with hyphens) is the preferred format according to the ISO 8601 standard for date representation.

Example: 2025-03-20
%Y/%m/%d (with slashes) is also a valid date format, but it is less commonly used in ISO 8601-compliant systems. It's more of a regional format, often used in some European and North American contexts, but not the canonical ISO 8601 format.

## Research - logging

```chatGPT
1. Setting Up Logging (logging.basicConfig())
You only need to configure the logging once in your application. Typically, this is done at the entry point of your application, which in your case seems to be at the scripts level.

2. Creating a Logger (logging.getLogger(__name__))
You should create a logger in each module that needs it.

__name__ will make the logger's name match the module name, which helps with understanding where log messages are coming from when you're troubleshooting.

3. Using the Logger (logger.debug(), logger.info(), etc.)
Once you have a logger set up in each module, you can use it to log messages.

Note: in practice, you will often use logger.debug() in larger applications to ensure you have control over where logs are coming from, but logging.debug() is a useful shortcut for simple scenarios where you don't need to create a logger.
```

## Research - avoiding SQL injection

```chatGPT

def add_preds_data(self, model, date, pred):
        """Add preds data to the database."""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT OR REPLACE INTO preds (model, date, pred)
                VALUES (?, ?, ?)
                """, (model, date, pred))
            conn.commit()

The main reason for using parameterized queries with placeholders (like ?, ?, ?) is to avoid SQL injection and ensure safety, which is especially important when dealing with user input. Even if you're using data from pandas, it’s still best practice to use parameterized queries for inserting data into your SQLite database. This approach is safer and more efficient than directly inserting values with format strings:

Security: Directly inserting values via string formatting (e.g., f"INSERT INTO table VALUES ({value1}, {value2})") exposes your code to SQL injection vulnerabilities. With placeholders (?), SQLite handles escaping for you.

Readability and Maintainability: Using placeholders helps keep the code clean and makes it easier to maintain, especially if the number of parameters changes or if you're adapting to a different database system.

Efficiency: Inserting with placeholders and parameterized queries is generally more efficient, as SQLite can optimize execution plans and avoid redundant parsing.

If you were to move to PostgreSQL, the code and approach you have using placeholders (?) would need a small adjustment, as PostgreSQL uses a different syntax for parameterized queries. SQLite uses ? as the placeholder for parameterized queries. PostgreSQL uses numbered placeholders like $1, $2, $3, etc. So, for PostgreSQL, your code would look like this:

def add_preds_data(self, model, date, pred):
    """Add preds data to the database."""
    with self._connect() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO preds (model, date, pred)
            VALUES ($1, $2, $3)
            ON CONFLICT (model, date) 
            DO UPDATE SET pred = EXCLUDED.pred;
            """, (model, date, pred))
        conn.commit()

Key Changes:

Placeholders: You replace ? with $1, $2, $3, and so on. These placeholders represent the parameters in the same order they are passed in the tuple (model, date, pred).

ON CONFLICT clause: In PostgreSQL, if you want to do an "upsert" (insert or update if a conflict occurs), you would typically use the ON CONFLICT clause, which handles conflicts on a unique or primary key (like (model, date) here). This is similar to SQLite’s INSERT OR REPLACE, but the syntax differs.
```

## Research - cron, task scheduler and systemd

Edited ChatGPT output:
```

On Windows: Task Scheduler
Open Task Scheduler - Press Win + R, type taskschd.msc, and hit Enter.
Create a New Task - Click "Create Basic Task" (or "Create Task" for more control)
Give it a name (e.g., DailyPythonScript)
Click Next and choose "Daily", then set the start time.
Set the Action - Choose "Start a Program".
Browse to your Python executable (e.g., C:\Users\YourName\AppData\Local\Programs\Python\Python3x\python.exe).
In the "Add arguments" field, enter the path to your script: "C:\path\to\your_script.py"
Set Working Directory (Optional but Recommended) - In "Create Task" → "Actions" → "Edit Action", ensure "Start in" is set to your script’s folder.
Run with the Correct User Permissions - If your script needs admin privileges or access to certain files, check "Run with highest privileges".
Save & Test - Right-click the task → "Run" to test.


You can configure Task Scheduler to run missed executions if the computer was off.
Find your task, or create a new one.
Go to the Settings tab.
Check "Run task as soon as possible after a scheduled start is missed".

Capturing/Redirecting Log Output
Method 1:
Modify the "Add arguments" field when setting up the task:
"C:\path\to\your_script.py" >> "C:\path\to\logfile.log" 2>&1
>> logfile.log → Appends standard output.
2>&1 → Redirects errors to the same log file.

Method 2: Enable Task History
In Task Scheduler, click "Enable All Task History" (on the right panel).
Right-click your task → "Properties" → "History" tab to check past runs.

---------------

On Linux: Cron Jobs
Open Crontab using bash: crontab -e
This opens the crontab (a list of scheduled jobs).
Add a Daily Job At the bottom, add a line like:
0 6 * * * /usr/bin/python3 /home/user/your_script.py
This runs the script every day at 6 AM.
0 6 * * * → 6:00 AM every day
/usr/bin/python3 → Path to Python (find it with which python3)
/home/user/your_script.py → Path to your script
Save & Exit - In nano, press Ctrl + X, then Y, then Enter.
Check if It’s Scheduled - Run crontab -l to see your scheduled jobs.
Check Logs if Needed If the job isn’t running, check logs:
grep CRON /var/log/syslog  # For Ubuntu/Debian
journalctl -u cron         # Another way to check
Use a Virtual Environment: Instead of python3, use /home/user/venv/bin/python3 if using a virtual environment.
Logging: Redirect output to a log file to track execution: 
0 6 * * * /usr/bin/python3 /home/user/your_script.py >> /home/user/script.log 2>&1

---------------

On Linux, systemd is a powerful service manager that can be used to run your Python script daily, providing better logging, restart policies, and dependency management than cron.

1. Create a systemd Service File in bash: sudo nano /etc/systemd/system/daily_script.service

Paste the following:

[Unit]
Description=Run my Python script daily
After=network.target

[Service]
User=yourusername
WorkingDirectory=/home/yourusername
ExecStart=/usr/bin/python3 /home/yourusername/your_script.py
Restart=on-failure
StandardOutput=append:/home/yourusername/daily_script.log
StandardError=append:/home/yourusername/daily_script.log
User=yourusername → Runs the script as your user.
Restart=on-failure → Ensures the script retries if it fails.
StandardOutput & StandardError → Logs output/errors to daily_script.log

Save and exit (Ctrl + X, then Y, then Enter).

2. Create a Timer to Run It Daily

sudo nano /etc/systemd/system/daily_script.timer

Paste the following:

[Unit]
Description=Run daily_script.service once per day

[Timer]
OnCalendar=*-*-* 06:00:00
Persistent=true

[Install]
WantedBy=timers.target
OnCalendar=*-*-* 06:00:00 → Runs every day at 6:00 AM.
Persistent=true → Runs missed executions when the system is powered on.

Save and exit.

3. Enable and Start the Timer

sudo systemctl daemon-reload
sudo systemctl enable daily_script.timer
sudo systemctl start daily_script.timer

4. Verify It's Working

Check timer status:

systemctl list-timers --all | grep daily_script

Manually trigger a run for testing:

sudo systemctl start daily_script.service

Check logs:

journalctl -u daily_script.service --no-pager --since today

Why Use systemd Instead of Cron? Cron Jobs vs systemd Timers
Logging:	Needs manual setup (>> logfile 2>&1) vs Built-in (via journalctl)
Error Handling:	No automatic retries	vs Supports Restart=on-failure
Missed Runs:	Skipped if system was off	vs Runs missed executions (Persistent=true)
Dependency Control:	Runs independently	vs Can start after network/db (After=network.target)
```

## Email notifications

Started looking through [https://realpython.com/python-send-email/](https://realpython.com/python-send-email/) 

Initial thoughts are
* likely need to set up a new gmail account
* probably worth looking at the OAuth2 credentials process
* add dotenv with password


## Repo Structure

Decided to see how well ChatGPT would fare with suggesting a structure. Prompt: 

```
I am creating a repo for a project called "Happy Plants: A data-driven predictive watering notification system". I have a brief description of the project as follows:

Project aim
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

To start with, give me a few thoughts about how I might structure my python code within this repo to suit the various aims. For example, I could have my code in a folder, named...? I could have a .py file for scraping the data and a separate one for training the RL model? I could use Jupyter notebooks when sourcing the data and/or prototyping this, but have a .py file that will be easier to use with automation tools? I could set up my RL model in a particular manner to allow for future automation, training etc, and this would involve...? I'm really just after ideas for setting things up in a way that will allow the project to evolve efficiently.
```

## Initial Research

https://github.com/ropensci-archive/bomrang?tab=readme-ov-file - bomrang package was an R package but has been archived due to "BOM's ongoing unwillingness to allow programmatic access to their data and actively blocking any attempts made using this package or other similar efforts"
https://docs.ropensci.org/weatherOz/ - R package that faciliates access to climate data from 3 sources including BOM FTP server
http://www.bom.gov.au/catalogue/anon-ftp.shtml - BOM FTP server
"All products available via the anonymous FTP service are subject to the default terms of the Bureau's copyright notice: you may download, use and copy that material for personal use, or use within your organisation but you may not supply that material to any other person or use it for any commercial purpose. Users intending to publish Bureau data should do so as Registered Users."
"the most reliable way to connect to the FTP server is with an FTP Client"

## 7 day Sydney forecasts

http://www.bom.gov.au/nsw/forecasts/sydney.shtml

Shows daily forecasts for the coming week
Gives % chance and possible rainfall range if chance is >=30%, but not when chance of rain is <=10%, unclear where the cutoff is (could be 20% for example)
Can use scraper to get both % chance and mm, could potentially get "cloudy" "mostly sunny" along with min/max temperature, but probably overkill?

## Historical daily rain

http://www.bom.gov.au/climate/rainfall/
Can change to table and filter for station 
Observations were drawn from Sydney Airport AMO {station 066037}

http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_stn_num=66037

"Observations of Daily rainfall are nominally made at 9 am local clock time and record the total for the previous 24 hours. Rainfall includes all forms of precipitation that reach the ground, such as rain, drizzle, hail and snow."

From Chrome > Developer Tools > Network > Response
http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_stn_num=66037

Then parse html response to extract the daily rainfall figures, with columns for each month, days of month as rows
e.g.
<tr>
            <th scope="row">16th</th>
            <td class="no-qc">35.6</td>
            <td class="no-qc">0.2</td>
            <td class="no-qc">0</td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
        </tr>

Has the data for 16 jan 25 = 35.6, 16 feb 25 = 0.2, 16 mar 25 = 0 and no data for apr 25 onwards

Changing the drop down from 2025 to 2024 gave
http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2024&p_c=-872183758&p_stn_num=66037

i.e. base url is http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av

from chatGPT

a) p_nccObsCode

This parameter specifies the type of observation data to retrieve. The values correspond to different weather observation categories. For example, p_nccObsCode=136 retrieves daily rainfall data, while p_nccObsCode=139 retrieves daily temperature data. 
THEDATASCHOOL.COM.AU

b) p_display_type

This parameter determines the format in which the data is presented. Common values include:

dailyDataFile
dataFile
conditions
dailySummary

c) p_c

This parameter is less documented, and its exact purpose isn't clearly specified in available sources. It might be a session identifier or a checksum used to validate requests. To determine its exact function, you could:

Monitor network traffic using Chrome Developer Tools to see how the value of p_c changes with different selections.

2025 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_stn_num=66037
2024 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2024&p_c=-872183758&p_stn_num=66037
2023 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2023&p_c=-872183758&p_stn_num=66037
2024 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2024&p_c=-872183758&p_stn_num=66037
2025 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2025&p_c=-872183758&p_stn_num=66037
(opened new browser window, went to initial URL above then changed year parameter)
2023 http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2023&p_c=-872183758&p_stn_num=66037

can't use incognito session with current settings as not https

Try visiting the site again tomorrow and see if the p_c parameter changes

http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2024&p_c=-872184033&p_stn_num=66037
http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av?p_nccObsCode=136&p_display_type=dailyDataFile&p_startYear=2023&p_c=-872184033&p_stn_num=66037

Note the p_c value has changed, so may need to browse to the URL without p_c and then look at a return value to allow for extracting more... or just keep the history in the database so we're only ever querying the latest year once

## Reasonable benchmark for required mm of rain

### ChatGPT professional opinion

I have some Syzygium smithii (formerly Acmena smithii) x15 that I planted in Aug 2022, and it's now Mar 2025, so they're about 2.5 years old. Give me an estimate of their water requirements, in mm of rainfall required over a given time period. This is a benchmark that will be used in a model I'm building, where I want to ensure they get a given amount of water, and if it doesn't rain enough, I'll get notified that I might want to manually water them.

ChatGPT said:
For Syzygium smithii (Lilly Pilly) at 2.5 years old, a reasonable benchmark for water requirements is:

Young (0-1 year): 25–40 mm per week
Establishing (1-3 years): 15–25 mm per week
Mature (3+ years): 10–15 mm per week (depending on soil, climate, and rainfall patterns)
Since yours are 2.5 years old, they are transitioning from the "establishing" to "mature" phase. Given your sandy soil, which drains quickly, you should aim for the higher end of the range:

Target: 20–25 mm per week (or ~80–100 mm per month).
For your model, sum the weekly rainfall and compare it to this benchmark. If the total falls short, you might need to supplement with irrigation.

### Approach

Each day, get a negative reward if mm of rainfall in past week + any manual watering is less than 20 mm. 

Need to look at the drip hose and estimate how many mm of water will come from a 30 minute session of watering. 

Then need a negative reward for asking to manually water, which needs to be calibrated based on user_lazy_score

## SQLAlchemy

Came across this while looking at an idempotent solution, to avoid duplicates in my data if the function gets run multiple times, or includes historical data that is already in the database. From ChatGPT:

* It allows you to write database-agnostic code. With SQLAlchemy, you can easily switch between different databases (e.g., SQLite, PostgreSQL, MySQL) by just changing the connection string, without needing to rewrite the SQL queries.
* SQLAlchemy provides features to help prevent SQL injection attacks by automatically escaping inputs in queries and using prepared statements.
