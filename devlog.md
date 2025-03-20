
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

# Historical notes

These are broadly in reverse chronological order (i.e. oldest stuff is at the bottom)

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
