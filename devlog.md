
# About

This file is for keeping assorted notes along the way, which may be useful in later blog / documentation, retracing steps to debug or recreate similar in the future etc

# To Do

## Outstanding items

A place to park ideas for future work, to allow me to better focus on the task at hand

  - mlflow - for tracking model performance over time
  - pydantic - for structured config management
  - terraform folder
  - what happens if the BOM change their forecast page html? need a way to pick this up (python error handling and/or check data looks reasonable) and notify that things are broken (part of the automation script phase of the project)
  - more generally, go over everything with an error handling perspective (may be overkill for a project designed to demonstrate familiarity with tools such as terraform rather than python web scraping)
  - revisit the add_src_to_path.py issue, with src not being treated as a module even if __init__.py is included in it
  - consider whether to adjust code to allow for intra-day data collection in the database (with optional parameter driving this) e.g. for collecting data every 1 hour for a week in order to understand a) how often they update forecasts (both time of day and frequency within the day and whether it's regular (automated) or not (manual) b) how "rest of day" forecasts change in response to actual weather events on the forecast day (i.e. if it rains half way through the day and then clears up, will the forecast amount reduce to zero as it's already rained or will the forecast amount approach the actual amount as the day progresses)
  - consider whether to share the data folder; not usually done but in this case it takes time to build up a history of forecast data and someone wanting to play with the system might not want to sit on it for 3 months locally. might be worth having a separate location with a copy of the data used for training the models that can also be used if someone wants to play around more generally
  - place benchmark amount in a config file somewhere so it's not spread across multiple files
  - adjust email to include a link to the two data sources
  - adjust viz to include min/max rain chance? 

## Completed items

  - check that having recommended we water on 1/4 it doesn't also recommend it on 2/4 as I suspect this aspect may have broken along the way  DONE 3/4/25
  - adjust email subject to include the day of the week and/or differ based on model prediction (e.g. "You should water your plants today" vs "Daily rainfall update")?  DONE 3/4/25
  - update Readme with details of how to replicate the process (particularly the need for a GCP project to send emails) DONE 3/4/25

# Historical notes

These are broadly in reverse chronological order (i.e. oldest stuff is at the bottom)

## Fixed auth flow

Seems we don't have indefinite refreshes and it may be 50 per user per app. This puts a spanner in the works of the server approach. Adjusted code for now to reauth as required, but only really works locally. Will have to revisit the email issue when we go to server, likely using own domain etc.

## Historical data definition

I probably should have paid more attention to the fine print when looking at the data page:

> Observations of Daily rainfall are nominally made at 9 am local clock time and record the total for the previous 24 hours.

This probably means running the process at 7:30am is missing out on useful information. However, I also like to water my plants well before 10am when evaporation and burning become factors. It's unclear how long they might take to update the site after the 9am measurement. Probably fine to leave as-is for now.

## Late night check

On 29/3/25 it rained a lot. I tried to run the daily_run.py at 11:30pm having run it earlier in the day. I actually got an error which I don't have time to look into right now (I need to go to sleep) but traceback is below:

Traceback (most recent call last):
  File "d:\Projects\happy-plants\scripts\daily_run.py", line 95, in <module>
    get_data()
  File "d:\Projects\happy-plants\scripts\daily_run.py", line 42, in get_data
    df_historical = historical_data()
  File "D:\Projects\happy-plants\src\get_data.py", line 157, in historical_data
    df = _extract_historical_data(soup=soup)
  File "D:\Projects\happy-plants\src\get_data.py", line 141, in _extract_historical_data
    date = datetime(int(year), month_number + 1, day_number).strftime('%Y-%m-%d') # add year and format as yyyymmdd
ValueError: day is out of range for month

I think what's happened here is that today is the 29th of March and there was no 29th of February. My code assumes the values are all populated. This will need a fix, as it will happen again tomorrow.

Fixed with a try.. except.. and confirmed that the error was that it was trying to populate 29/2. There may be a better way, but I need to sleep.

Interestingly, on the Forecast data page, the forecast was issued at 4:20pm and simply has 80% chance of any rain with no possible rainfall range.

## Minimum rainfall is actually used

As at 9:30AM on Fri 28/3/25, the forecast for today is 1-10 mm and tomorrow is 20-70mm, so the min mm, while almost always 0mm, does actually take values >0mm from time to time. Luckily the data is being saved to the database, so I can always decide to add it into prepare_data.py and/or create_plots.py at some point in the future.

## Adding source to path

I had add_src_to_path.py in my scripts folder and removed it to make things more tidy. I'm putting the code here as a reminder to consider discussing this in blog post

```python
# This file dynamically adds the 'src' folder to sys.path at runtime, so import database will work given src/database.py
# You then add "import add_src_to_path" to the top of another .py file in the scripts folder to enable this functionality

# Alternative approach is to use .vscode/settings.json with the following
# Pros: linting will work properly, simpler code with one less import file
# Cons: assumes user is using vscode, otherwise things might not work
# Going with the .vscode approach for now, but will revisit this if/when we start deploying it to a server
'''
{
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}/src"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}/src"
    },
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "${workspaceFolder}/src"
    },
    "python.autoComplete.extraPaths": [
        "${workspaceFolder}/src"
    ],
    "python.analysis.extraPaths": [
        "${workspaceFolder}/src"
    ]
}
'''
import logging
logger = logging.getLogger(__name__)

import sys
import os

# Dynamically add 'src' to sys.path at runtime
logging.debug(f'current working directory is {os.getcwd()}')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logging.debug(f'project_root is {project_root}')
src_path = os.path.join(project_root, 'src')
logging.debug(f'src_path is {src_path}')
if src_path not in sys.path:
    sys.path.append(src_path)
    logging.debug(f'added src_path to sys.path')
```

## Notes for blog

Another place to jot down some things I might want to talk about later

* Logs are great, particularly at the point where you want to confirm that your Task Scheduler ran correctly even though you changed the name of the file from collect_data.py to daily_run.py

* Extensive use of ChatGPT to solve standard problems, which I probably could have figured out myself in the past, but which tends to produce high quality answers quicker than I would have come up with them myself, particularly when utilising abstractions in pandas and similar where I haven't read and memorised the entire docs and things are changing over time. Some examples:

  - To add a column that aggregates the past 7 days in my dataframe I'm using the following, which followed me providing a simple example of what I wanted using Excel: df_historical["rainfall_mm_week"] = df_historical["rainfall_mm"].rolling(window=7, min_periods=7).sum()

  - Initially my database.py had many functions that had something similar at the top, allowing for a custom path. I decided it would be sensible to use a class based structure. While I could have done this myself, it was something that ChatGPT was actually able to do for me essentially instantaneously.

* Tendency to want to revisit things as I learn more - applies to both blog posts and to code. Examples:

  - initial blog post as "career plan", but this is a live document, so I have a conversation and make a change and went back and adjusted my post to reflect this, but at some point I have to draw the line and accept that it's a historical artifact

  - learning about best/better practices for docstrings, finding/improving my own style over time, resisting the urge to go back and rework all my docstrings (or deciding to do so, at some cost but to ensure anyone looking at the code gets the best/most accurate impression of where I'm now at)

* Why is it useful to have all 7 days of forecast data if we're just going to look at the past 6 days and make some judgement about the chance of rain today? Well actually, if my plants haven't had water in 6 days and it's not raining today, but it IS raining tomorrow, I probably won't bother raining today. A RL model can take into account my (custom, high) level of laziness and potentially make this judgement call on my behalf, whereas a simple rule based system won't. A regular machine learning algorithm also won't take this approach, unless I build it into my target variable somehow, in which case why not just apply the simple rule based approach? OK so I've justified the potential (probably small) benefit of using RL, but why bother using a ML algorithm here? I guess we expect that it will handle the probabilities involved, and for example, the forecasts may consistently be wrong, for example they may overstate the chance of rain to avoid people being grumpy if they say it won't rain, but this may mean our model should suggest watering even if the chance is 80%, because they always say it's 80% when it's actually 40%.

* This post is the first in a series relating to the Happy Plants project. ... This first post will cover everything involved in building a data-driven notification system on my local Windows computer. This includes features such as using web scraping to source the data, saving the data in a database, processing the data to be ready for the algorithm to make a decision, the ability to send email notifications, and automation using Windows Task Scheduler to run everything on a daily basis.
  * Later posts will cover moving the application to a cloud provider, using machine learning algorithms, and potentially testing/comparing algorithm performance.
  * (maybe don't include all the details below in the first post, until the work itself has been done)
  * The second post will cover everything involved in moving the system into the cloud. This includes features such as AWS (or GCP) basics, Terraform (or similar), and automation using Linux cron (or systemd) and/or some other CI/CD approach.
  * The third post will cover a few different machine learning algorithms, including reinforcement learning.

## Thoughts on real world customisation (for blog)

I'm conscious that this "simple" problem has a habit of becoming less simple at every turn, if I let myself overthink things. For example:

* I'm assuming that when the model tells someone to manually water, they will do so. In practice, people might get the notification and ignore it, but want further notifications to keep reminding them rather than have their plants die over the coming week if it doesn't rain, or feel they need to water their plants a day or two later when the model would actually tell them not to bother given the delay. A solution to this might be to let the user click something in their email to confirm they've watered it, then in my project I need functionality to record this event and only replace historical data when the user actually watered their plants. None of this is hard, but I need to **not** fall into the trap of doing such things at this point when I'm just trying to demonstrate the basics.

* It's a toy problem, so I can pick up and process the full history. But if it weren't a simple project, perhaps it would be worth my time to filter the history. I'm trying to demonstrate good practices, but probably no-one will actually look at my code or use it for the more complex scenario, so even if it doesn't take long to add this in, I *probably* should refrain from doing so.

* In database.py I have a class which allows the user to flexibly define the location of the database, while also having a default location, and would be relatively straightforward to swap out an sqlite database for something like postgres. It's great that I'm demonstrating my knowledge here, and the product is better, but I'm of two minds whether it would have been better to simply stick to a single database location and format without the flexibility, which is quicker to develop and gets the job done, but doesn't demonstrate my understanding as well

## Cleaning up debug logging

Something to ponder about further:

```chatGPT
When people use logger.debug while creating their code, do they tend to delete a lot of these once their code is working? and/or comment it out?
ChatGPT said:
It depends on the developer and the project, but there are a few common patterns:

Leaving Debug Logs in Place – Many developers keep logger.debug statements in their code, especially in complex logic, so they can enable debug logging later if needed. Since logging frameworks usually allow adjusting the logging level dynamically (e.g., setting INFO or WARNING in production), debug logs can stay without affecting performance.

Removing Unnecessary Logs – Some developers clean up excessive debug logs once the code is stable, particularly if they were only useful for initial debugging. This helps keep the codebase cleaner and avoids unnecessary log noise.

Commenting Out Logs – Some people comment out debug statements instead of deleting them, just in case they need them later. This is more common in less formal workflows but is generally discouraged because commented-out code can clutter the codebase.

Using Conditional Debugging – Instead of removing debug logs, developers sometimes wrap them in conditions (e.g., if some_debug_flag: logger.debug(...)). This allows selective logging without modifying the code.

Best practice is to keep useful logger.debug statements but ensure logging is configured properly so they don’t pollute production logs.
```

## User snippets

F1 > Snippets > Configure snippets e.g.

	"Log Debug Statement": {
		"prefix": "log",
		"body": "logger.debug(f\"$1 {}\")",
		"description": "Insert a logger.debug statement"
	}

## Modelling approach

Approach
* pick up the historical days leading up to the forecast day
* pick up all forecast_applies_to data for the date_forecast_was_made day
* Flatten both of these, using the difference between the date and the forecast date to produce an index
* Then keep the relevant ones (e.g. past X days, next Y days)
* "feature selection" e.g. if the success criteria is 20mm per week, add up the watering for the past 6 days
as this is guaranteed (and includes adjustments for assumed action taken following prior watering notifications)
and/or add up some expected rainfall (e.g. rain_chance * average of rain_mm_low and rain_mm_high, for next 1 day or possibly 
each future day. 
Relevance of this aspect might depend on what model(s) I'm using. In the short term we might go with something super simple
(e.g. just use actual past 6 days + expected for next 2 days and issue notification if <20mm), particularly while
collecting/generating data and setting up notification flow

Assumptions / Areas of uncertainty
* include current day forecast?
  - time of day that the program is run (e.g. running at the start of the day vs at the end of the day)
  - time of day that the forecasts are released (e.g. is this 9am? 6am? 12am? are they updated throughout the day? on an hourly basis?)
  - wording implies it's for the remainder of the day which could be misleading (e.g. it rains all morning, then forecast is 0.0)
  - ideal time of day to run this might depend on when the user is going to take action (e.g. free to water at 7am vs 10am vs 6pm)
* assume that past notifications resulted in watering at the required amount (need to overwrite historical data after extracting it)

Note on the forecast page
http://www.bom.gov.au/nsw/forecasts/sydney.shtml
it actually has e.g. 
"Forecast issued at 4:20 pm EDT on Thursday 20 March 2025."
so looking at this page a few times manually will probably give sufficient info to get a feeling for this
particularly if it's a day where it's been raining and clears up

At 7am, 9am:
Forecast issued at 4:45 am EDT on Friday 21 March 2025.
70% chance of rain with 0 to 7 mm of rain

At 10am:
Forecast updated at 9:29 am EDT on Friday 21 March 2025.
70% chance of any rain, does not show the possible rainfall figures

At 2pm:
Forecast updated at 11:09 am EDT on Friday 21 March 2025.
70% chance of any rain

Might actually be more sensible to include forecast rainfall from yesterday for today, then use forecast rainfall for future days from today (a bit complicated but possibly the most appropriate approach)

## Research - dates in databases

For database purposes, it's typically better to use %Y-%m-%d (full year) since it's the ISO 8601 standard format and more commonly recognized by most systems.

ISO 8601 defines a standardized format for representing dates, and both %Y-%m-%d and %Y/%m/%d are valid date representations, but with a slight difference in separator:

%Y-%m-%d (with hyphens) is the preferred format according to the ISO 8601 standard for date representation.

Example: 2025-03-20
%Y/%m/%d (with slashes) is also a valid date format, but it is less commonly used in ISO 8601-compliant systems. It's more of a regional format, often used in some European and North American contexts, but not the canonical ISO 8601 format.

For pandas calculations, having dates in datetime format yyyy-mm-dd 00:00:00 is useful. I'm undecided if it makes sense to store the 00:00:00, considerations:
  - outputs are more verbose
  - would need to test filtering e.g. does something like "= 'yyyy-mm-dd'" still work or do you need "= 'yyyy-mm-dd 00:00:00'"
  - currently using date as PK so process is idempotent for forecasts within a given day. would likely need to remove prior ones on rerun within a given day, or just fix the time component to 00:00:00 regardless of when it's actually run

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

Using 
```python
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
```
Adds timestamps and makes it easier to understand logs with similar values being appended over time (e.g. collect_data.py being run every day)

Reflection:
It's all working and I better understand the options now. I'm still on the fence with regard to whether it's better to configure the log destination in TS/cron vs within python. When developing, it feels nice to be able to run the script in a terminal and see the logging output and not have to open the log file. I'm also of two minds about whether it's good to have a block of ~10 lines of complex code to set up the logger properly and add src folder to the path, having to copy this code between scripts, vs having this be part of the TS/cron stage and/or having a central script (e.g. config.py) that can be called by the other scripts so this complexity is hidden away and can be adjusted/copied between projects more easily. It feels good to be able to customise the logging levels at each script and only have it direct to a file once the script is essentially done. Lots of options and tradeoffs to consider.

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

## Research - task scheduler, cron and systemd

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

Notes from doing this in practice:
* Point the executable to the python.exe in the virtual environment 
* Use quotes if there’s any possibility of spaces
* Backslashes (\) are standard for Windows, but forward slashes (/) also work
* Anecdotally, Start In (Working Directory) does not accept quoted paths. If you add quotes, Task Scheduler may fail to execute the task.
* In "add arguments", paths with spaces must be quoted in the arguments field because it treats them as separate parameters otherwise

Create Task - General
* Name: gather_rainfall_data
* Triggers: Daily, starting today at 7:30am
* Actions: 
Program/script: C:\.venv\happy_plants\Scripts\python.exe 
Add arguments: "D:\Projects\happy-plants\scripts\collect_data.py" >> "D:\Projects\happy-plants\scripts\taskschd.log" 2>&1
Start in: D:\Projects\happy-plants
* Conditions: Network - start only if my wifi network connection is available
* Setting:
check "Run task as soon as possible after a scheduled start is missed"
check "If the task fails, restart every" and set to 2 hours (in case of internet outage)
adjust "Stop the task if it runs longer than" to "1 day" (3 days seems a bit excessive)
and/or adjust "If the task is already running, then the following rule applies" to "Stop the existing instance" (given default is to allow task to run for 3 days)

check/debug:
C:\.venv\happy_plants\Scripts\python.exe "D:\Projects\happy-plants\scripts\collect_data.py" >> "D:\Projects\happy-plants\scripts\taskschd.log" 2>&1
DOES NOT OUTPUT LOGS - because the >> redirect works in cmd.exe not in python.exe
cmd.exe /c C:\.venv\happy_plants\Scripts\python.exe "D:\Projects\happy-plants\scripts\collect_data.py" >> "D:\Projects\happy-plants\scripts\taskschd.log" 2>&1
note /c tells cmd.exe to run a command and exit

Once task is created you can see it under "Task Scheduler Library"

Notes
* You need to manually right click Task Scheduler Library and Refresh to see e.g. Status "Ready"



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

Started looking through [https://realpython.com/python-send-email/](https://realpython.com/python-send-email/) and chatting with Copilot. 

This is a tricky design decision:
* Amount of setup time required of me up front
* Amount of setup time required of someone picking up my codebase/solution
  - can mitigate somewhat with clear documentation
* Limitations or costs associated with third party providers
  - using or not using third party providers has pros/cons for me personally
    in terms of demonstrable skills
* Packages included in the requirements.txt to handle APIs

Options:
* use Gmail with App Passwords ("allow less secure apps" is depreciated)
  - applies to account, potentially requiring multi-account setup/management
    or the user accepting a lower level of security on their account
* use Gmail with OAuth2
  - requires user to set up a Google Cloud project for API keys
  - requires more complex codebase
* use third party provider (e.g. SendGrid, Mailgun)
  - limits on free emails and/or cost

Looks like you can send 100 emails / day for free with no credit card using Twilio/Sendgrid. Seems simple compared to the burden of setting up a GCP project and/or downgrading Google account security. If you wanted to scale it, you might start using GCP and Gmail, but then you might also be able to more easily justify the cost of using the third party provider with built in analytics.

Set up a Twilio account. It's honestly a bit of a burden as you have to verify phone numbers, create sender IDs etc. Unclear that this is really the silver bullet compared to setting up a Gmail account for example. Twilio does highlight various channels, so could be useful to send SMS or WhatsApp communications using the same platform.

Approach:
* start with free Twilio account 
* consider going down the "set up my own SMTP" and/or "use Gmail API with GCP project" route in due course

History
* create Twilio account, including phone number verification
* go to SendGrid via Twilio, had to again enter phone number
* Create a Sender
  - because Twilio is designed for mass marketing in different regions, you have to have physical company address etc to comply with anti-spam laws
  - using a personal gmail email address will likely fail due to [DMARC](https://www.twilio.com/docs/sendgrid/ui/sending-email/dmarc) "Gmail, or any other receiving email server, has no way of knowing whether you are using SendGrid to send email for legitimate purposes or spoofing Yahoo's domain"
  - hence, you need to [authenticate a domain you own](https://www.twilio.com/docs/sendgrid/ui/account-and-settings/how-to-set-up-domain-authentication)
    - DNS is a naming system for domains on the internet. It resolves domains humans can remember, like sendgrid.com, to IP addresses that belong to specific computers
    - your domain may have...CNAME records pointing to the cloud service that handles your email
    - DNS records are managed using your DNS provider or host. Popular DNS providers include...Cloudflare



| Option | Pros ✅ | Cons ❌ | Considerations 🔹 |
|--------|--------|--------|------------------|
| **1. Gmail SMTP (App Passwords)** | - Free and easy to set up  <br> - Works with a separate Gmail account | - Requires enabling App Passwords  <br> - Sending limits (500 emails/day for free Gmail)  <br> - May have deliverability issues | - Use a separate Gmail account, not your main one. <br> - Best for low-volume personal use. |
| **2. Gmail SMTP (OAuth2)** | - More secure than App Passwords  <br> - No need to store plain-text credentials | - More complex setup (requires Google Cloud project)  <br> - Others cloning your repo must set up OAuth | - Only use if security is a primary concern. <br> - Less convenient for a simple script. |
| **3. Own Mail Server** | - Full control over sending emails  <br> - No third-party service required | - Requires setting up SPF, DKIM, and DMARC  <br> - Many cloud providers block SMTP port 25  <br> - Complex to maintain | - Only feasible if you own a domain and are comfortable managing email infrastructure. |
| **4. Transactional Email Service (SendGrid, Mailgun, etc.)** | - High deliverability and reliability  <br> - Free tiers available  <br> - No SMTP port issues | - Requires account verification  <br> - Often requires domain authentication for best results | - Best for sending emails reliably in production. <br> - Needs a domain for optimal setup. |
| **5. SMTP Relay (e.g., AWS SES, Postmark SMTP)** | - More reliable than personal SMTP  <br> - Easier than running your own mail server | - Requires setting up SMTP credentials  <br> - May require domain verification | - Good middle ground for cloud-based apps. <br> - AWS SES is cheap and scalable. |
| **6. Pre-Built CLI Tool (mailx, msmtp, etc.)** | - Simple if on Linux  <br> - Uses system mail settings | - Not cross-platform (Windows setup is tricky)  <br> - Requires configuring outgoing mail | - Useful for cloud-hosted Linux setups. <br> - Not ideal for cross-platform scripts. |

My approach will be
1. Set up Gmail SMTP (App Passwords) as it seems like a relatively simple option that others can test out if they want to
2. If/When I purchase a domain name for the blog, go down the "Own Mail Server" rabbit hole and provide this as a secondary method for this app to send emails.

Steps
1. Create a new Gmail account ([instructions](https://support.google.com/mail/answer/56256?hl=en))
  - note you need to write down the password when you create it as Google/Chrome won't automatically add it to the Google password manager
2. Enable 2-Step Verification & Generate an App Password
  - Google Account Security > "Signing in to Google" > enable 2-Step Verification (if not already enabled)
  - Google Account Security > App Passwords (this option only appears after enabling 2FA) > App: Mail and Device: Other (Custom name) > Enter a name (e.g., "Python Script") and click Generate > Copy the 16-character password (it won’t be shown again)
  - I can't find this, so I search and find the direct link: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
  - at this point I get "The setting you are looking for is not available for your account." 
  - From the Google instructions [here](https://support.google.com/accounts/answer/6103523?sjid=12133855215205350075-NC):
```
If you’ve set up 2-Step Verification but can’t find the option to add an app password, it might be because:
* Your Google Account has 2-Step Verification set up only for security keys.
* You’re logged into a work, school, or another organization account.
* Your Google Account has Advanced Protection.
```
- I'm not aware that any of the above apply, but it's getting to the point where I think we with Plan B as this isn't the "simple" option I was promised or want for someone having a play with this project.

In case I want to come back to it, here's the step-by-step guide from ChatGPT:

```
Step 1: Create a Separate Gmail Account (Recommended)
Since you don’t want to use your main Google account, follow these steps:

Go to Google Account Sign Up.

Create a new Gmail account (e.g., yourapp@gmail.com).

Log into this new Gmail account and enable 2-Step Verification (required for App Passwords).

Step 2: Enable 2-Step Verification & Generate an App Password
App Passwords allow your script to log in without needing your actual Gmail password.

Log into the new Gmail account.

Go to Google Account Security.

Under "Signing in to Google", enable 2-Step Verification (if not already enabled).

Once 2-Step Verification is enabled, go back to Google Account Security.

Click App Passwords (this option only appears after enabling 2FA).

Select App: Mail and Device: Other (Custom name).

Enter a name (e.g., "Python Script") and click Generate.

Copy the 16-character password (it won’t be shown again).

Step 3: Install Required Python Libraries
Ensure you have the necessary libraries installed:

sh
Copy
Edit
pip install smtplib email-validator
smtplib is built into Python, so no need to install it separately. The email-validator package is optional but useful for checking email validity before sending.

Step 4: Write Your Python Script
Here’s a basic Python script using Gmail’s SMTP:

python
Copy
Edit
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USERNAME = "yourapp@gmail.com"  # Use the Gmail address you created
GMAIL_PASSWORD = "your-app-password"  # Use the 16-character App Password

# Email details
sender_email = GMAIL_USERNAME
receiver_email = "recipient@example.com"  # Replace with the recipient's email
subject = "Test Email from Python"
body = "This is a test email sent from Python using Gmail SMTP."

# Create the email message
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))

# Send email using SMTP
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
Step 5: Test the Script
Run the script in your Python environment (python send_email.py).

Check the recipient’s inbox (and spam folder, just in case).

Step 6: (Optional) Improve Security
Do NOT hardcode credentials: Store them in environment variables instead.

Use a .env file: Install python-dotenv (pip install python-dotenv) and store credentials securely.

Example .env file:

ini
Copy
Edit
EMAIL_USER=yourapp@gmail.com
EMAIL_PASS=your-app-password
Modify the script to use these values:

python
Copy
Edit
import os
from dotenv import load_dotenv

load_dotenv()
GMAIL_USERNAME = os.getenv("EMAIL_USER")
GMAIL_PASSWORD = os.getenv("EMAIL_PASS")
```

Plan B: Oauth2 rabbit hole

Step 1: Create a Google Cloud Project
  - Go to [Google Cloud Console](https://console.cloud.google.com)
  - (optional) Swap to the new Gmail account you created (top right)
  - Select a project (top left; will be set to the last active project or "Select a project" if you don't have any existing ones) > "New Project" > add a name (e.g. "Gmail SMTP OAuth2") > Create > (wait a moment) Select project
    - Can use a generic name and reuse this project across multiple apps that require access to the same gmail, or name it specific to the app (more secure but more effort); recommendation is to make a generic until such time as you need it to be specific (due to scale, multiple users etc)
    - optionally rename the project ID to make it easier to type/remember/read (e.g. gmail-smtp-oauth2-465784 -> alexgouldblog-gmail-smtp)

Step 2: Enable the Gmail API
  - (within project) APIs & Services > Library > Gmail API (under "Google Workspace or use search box) > Enable

Step 3: Create OAuth 2.0 Credentials
  - APIs & Services > Credentials
  - (if prompted) Configure Consent Screen > Get started
    - App Information: Fill in app name (e.g. Alex Gould's blog) and user support email (your new Gmail address) > Next
    - Audience: External
    - Contact Information: your new Gmail address
    - Finish: (optional) take a look at the [Google API Services: User Data Policy](https://developers.google.com/terms/api-services-user-data-policy) (e.g. must have privacy/data policy for public apps, can't use Google Sign-In for Child/Mixed audience apps)
 - Create OAuth client > Application Type: "Desktop App" > Name (e.g. happy-plants) > Create > Download JSON (save as credentials.json in project folder)
    - added credentials.json to .gitignore

Step 4: Install Required Python Libraries
  - `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
    - renamed my src/email.py as this apparently conflicts with Python's built-in email module
    - added these to requirements.txt

Aside - read [the docs](https://developers.google.com/workspace/gmail/api/guides) at least briefly, as the specific code used changes over time, so ChatGPT may suggest weird things (e.g. it told me to pip install google-auth-oauth2l which isn't actually a package). Googling "python google gmail api" gets me to the [correct page](https://developers.google.com/workspace/gmail/api/quickstart/python) quickly.

```python
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
```





```ChatGPT
Step 5: Authenticate and Get an OAuth2 Token
  - create a Python script to authenticate and obtain an access token.

import os
import pickle
import base64
import google.auth
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth2 Scopes for sending email via Gmail SMTP
SCOPES = ["https://mail.google.com/"]

def get_oauth2_credentials():
    creds = None
    token_file = "token.pickle"

    # Load existing token if available
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    # If credentials are not valid, obtain new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh token if expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)  # Open browser for login

        # Save credentials for future use
        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return creds

# Run the authentication process
creds = get_oauth2_credentials()
print("OAuth2 authentication successful!")
What This Script Does
Loads the credentials.json file (downloaded from Step 3).

Opens a browser for Google sign-in (first-time setup).

Requests Gmail API access and saves the token (token.pickle).

Refreshes the token automatically when needed.

Step 6: Send Email Using OAuth2 and Gmail SMTP
Now, modify your email-sending script to use OAuth2 authentication.

python
Copy
Edit
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Load OAuth2 credentials
def load_credentials():
    creds = Credentials.from_authorized_user_file("token.pickle")
    creds.refresh(Request())  # Refresh token if needed
    return creds.token

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
GMAIL_USERNAME = "yourapp@gmail.com"  # Use your Gmail address

# Generate OAuth2 authentication string
def generate_oauth2_string(username, access_token):
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()

# Send email
def send_email():
    access_token = load_credentials()
    auth_string = generate_oauth2_string(GMAIL_USERNAME, access_token)

    sender_email = GMAIL_USERNAME
    receiver_email = "recipient@example.com"  # Replace with the recipient's email
    subject = "Test Email with OAuth2"
    body = "This email was sent using Gmail SMTP with OAuth2 authentication."

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.docmd("AUTH", "XOAUTH2 " + auth_string)  # OAuth2 authentication
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

send_email()
Step 7: Run and Test Your Script
Run the authentication script once:

sh
Copy
Edit
python authenticate.py
This will open a browser to sign in with your Gmail account.

Google will ask for permission to send emails on your behalf.

After granting access, the script will save your OAuth2 token in token.pickle.

Run the email-sending script:

sh
Copy
Edit
python send_email.py
This will use the OAuth2 token to send an email via Gmail’s SMTP server.

Step 8: (Optional) Set Up Token Auto-Renewal
The access token expires every 1 hour, but the refresh token allows it to be renewed automatically. The scripts above already handle token renewal, so you don’t need to manually log in again.
```



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

(but do I miss out on the understanding by abstracting things?)
(how often do you change from one SQL / DB to another and need to rewrite things vs having to learn SQLAlchemy and have other devs be familiar with it?)