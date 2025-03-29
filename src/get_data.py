"""
This script uses BeautifulSoup to scrape the public historical and forecast rainfall data from the BOM site,
saving it into a pandas dataframe with formatted dates.
"""

# Logging setup
import logging
logger = logging.getLogger(__name__)

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime

# General functions

def _get_page_source(url):
    """Return page source from url (pretending to be a Chrome browser)"""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page: {response.status_code}")

# Forecast data functions

def _convert_to_datetime(date_str, current_date=None):
    """
    Converts a forecast string (e.g., 'Friday 21 March') into a datetime object
    and returns the date in 'd/m/y' string format (e.g., '21/3/25').

    Args:
        date_str (str): The forecast string to be converted (e.g., 'Friday 21 March').
        current_date (datetime, optional): The current date to use for testing. Defaults to today's date.

    Returns:
        tuple: A tuple containing two strings:
            - date_forecast_was_made (str): The date the forecast was made, in 'd/m/y' format.
            - date_forecast_applies_to (str): The date the forecast applies to, in 'd/m/y' format.
    """

    if not current_date:
        current_date = datetime.today().date()

    # forecast for the remainder of the day on which the forecast is made
    if "Forecast" in date_str:
        forecast_date = current_date

    else:    
        month_day = date_str.split(' ', 1)[1] # remove the weekday portion
        current_year = current_date.year

        forecast_date = datetime.strptime(f"{month_day} {current_year}", "%d %B %Y").date() # read in as d mmm y
        if forecast_date < current_date:
            forecast_date = forecast_date.replace(year=current_year + 1)

    # format as yyyymmdd
    return current_date.strftime('%Y-%m-%d'), forecast_date.strftime('%Y-%m-%d')

def _extract_forecast_data(soup):
    """Extract rainfall chance and amounts from the Beautiful Soup class"""

    sections = soup.find_all(class_="day")
    results = []
    for section in sections:

        # extract the date (which is implied by the current date and this being a forecast for the coming week, includes rest of today)
        date_forecast_applies_to = section.find('h2').text.strip()
        date_forecast_was_made, date_forecast_applies_to = _convert_to_datetime(date_forecast_applies_to)

        rain_section = section.find_next('dd', class_="rain")
        rain_mm_low = 0
        rain_mm_high = 0
        if "Possible rainfall" in rain_section.text: # rainfall mm is only shown when rainfall chance exceeds some threshold
            rain_mm = rain_section.find_next('em', class_="rain").text.strip()
            match = re.search(r"(\d+)\s*to\s*(\d+)", rain_mm) # convert 0 to 3 mm into values 0 and 3 using regular expressions
            if match:
                rain_mm_low = int(match.group(1))
                rain_mm_high = int(match.group(2))

        rain_chance = rain_section.find_next('em', class_="pop").text.strip()
        rain_chance = float(rain_chance.strip('%')) / 100 # convert from text % to float now (might be easier than doing so later on)

        results.append([date_forecast_was_made, date_forecast_applies_to, rain_chance, rain_mm_low, rain_mm_high])

    df = pd.DataFrame(results, columns=['date_forecast_was_made', 'date_forecast_applies_to', 'rain_chance', 'rain_mm_low', 'rain_mm_high'])
    df['date_forecast_was_made'] = pd.to_datetime(df['date_forecast_was_made'], format='%Y-%m-%d')
    df['date_forecast_applies_to'] = pd.to_datetime(df['date_forecast_applies_to'], format='%Y-%m-%d')

    return df

def forecast_data(url = "http://www.bom.gov.au/nsw/forecasts/sydney.shtml"):
    """Return a pandas dataframe containing BOM rainfall forecasts"""

    src = _get_page_source(url)
    soup = BeautifulSoup(src, 'html.parser') # recommended to include html.parser here to ensure consistent cross-platform results
    df = _extract_forecast_data(soup=soup)
    return df

# Historical data functions

def _extract_historical_data(soup):
    """Extract historical rainfall by date from the Beautiful Soup class"""

    # Extract the year (from th with scope="col")
    year = soup.find('th', {'scope': 'col'}).text.strip()

    # Initialize the list for storing data rows
    data = []

    # Regular expressions pattern for checking to see if value is 1st .. 31st
    pattern = re.compile(r'^\d{1,2}(st|nd|rd|th)$')

    # Iterate over each table row in the tbody
    for row in soup.find_all('tr')[1:]:  # Skip the first row (graph row)
        row_data = []

        # check row exists and is one of the data rows (1st to 31st in the first column)
        th = row.find('th', {'scope': 'row'})
        if th:
            th = th.text.strip()
            if pattern.match(th):
                row_data.append(th)

                # extract the row data
                cells = row.find_all('td', class_='no-qc')
                for cell in cells:
                    cell_text = cell.text.strip()
                    if cell_text: # only append non-empty cells
                        row_data.append(cell_text)

                data.append(row_data)

    # convert data to a list with dates in the format dd/mm/yy
    daily_data = []
    for i, (day, *values) in enumerate(data):
        day_number = int(day[:-2]) # remove 'st', 'nd' etc
        for month_number, value in enumerate(values):
            try:
                date = datetime(int(year), month_number + 1, day_number).strftime('%Y-%m-%d') # add year and format as yyyymmdd
                daily_data.append([date, value])
            except: # quick fix for date out of range (e.g. trying to populate 29/2 once 29/3 exists)
                logger.debug(f"Unable to process date {int(year)}-{month_number + 1}-{day_number}")

    # convert data to dataframe for ease of filtering etc
    df = pd.DataFrame(daily_data, columns=['date', 'rainfall_mm'])
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df = df.sort_values(by='date', ascending=True)
    return df

def historical_data(base_url = "http://www.bom.gov.au/jsp/ncc/cdio/weatherData/av", p_nccObsCode=136, p_display_type="dailyDataFile", p_stn_num=66037):
    """Return a dataframe containing BOM historical rainfall data"""

    # probably overkill to parameterise this, but on the off chance someone wants to clone and run it using a different weather station...
    url = f"{base_url}?p_nccObsCode={p_nccObsCode}&p_display_type={p_display_type}&p_stn_num={p_stn_num}"
    src = _get_page_source(url)
    soup = BeautifulSoup(src, 'html.parser') # recommended to include html.parser here to ensure consistent cross-platform results
    df = _extract_historical_data(soup=soup)
    return df

if __name__ == "__main__":
    
    # Logging setup
    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    df_historical = historical_data()
    logger.debug(f"df_historical {df_historical}")