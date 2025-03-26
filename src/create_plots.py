'''Create plots of historical and forecast rainfall data'''

# Logging setup
import logging
logger = logging.getLogger(__name__)

# Paths relative to project root directory
import os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import database

# amount of water assumed to be administered in response to a historical notification that the user should water their plants
# should be consistent with the value in prepare_data.py
DEFAULT_WATER_MM=20

def plot_forecast(save_file=True, file_path="", file_name="my_image.png"):
    """Generate a forecast plot with three subplots: Historical Rainfall, Rain Chance, and Rain Amount

    Args:
        save_file (bool): whether to save the image as a file rather than displaying it (Default: True)
        file_path (str): location to save the image (defaults to img directory in project root)
        file_name (str): name of the file (Default: my_image.png)

    Returns:
        image_path (str): full path to the image that was generated (None if save_file is False)
    """

    if file_path == "":
        file_path = os.path.join(PROJECT_ROOT, 'img')
    image_path = os.path.join(file_path, file_name)
    
    db = database.RainfallDatabase()
    
    # Get historical data and filter for last 7 days
    df_historical = db.get_historical_data()
    df_historical["date"] = pd.to_datetime(df_historical["date"])
    last_7_days = df_historical["date"].max() - pd.Timedelta(days=6)
    df_historical = df_historical[df_historical["date"] >= last_7_days]
    
    # Get forecast data
    df_forecast = db.get_forecast_data()
    latest_forecast_date = df_forecast["date_forecast_was_made"].max()
    df_latest = df_forecast[df_forecast["date_forecast_was_made"] == latest_forecast_date]

    fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, ncols=1, figsize=(10, 12), gridspec_kw={'height_ratios': [1, 1, 1]})

    # see matplotlib colours here: https://matplotlib.org/stable/gallery/color/named_colors.html

    # First subplot: Historical Rainfall
    ax0.bar(df_historical["date"], df_historical["rainfall_mm"], color='royalblue')
    ax0.axhline(y=DEFAULT_WATER_MM, color='red', linestyle='dotted', linewidth=2)  # Add dotted red line
    ax0.set_ylabel("Rain amount (mm)")
    ax0.set_title("Historical Rainfall (Last 7 Days)")
    ax0.xaxis.set_major_formatter(mdates.DateFormatter('%a %d %b'))
    
    # Second subplot: Rain MM
    ax1.bar(df_latest["date_forecast_applies_to"], df_latest["rain_mm_high"], color='cornflowerblue')
    ax1.axhline(y=DEFAULT_WATER_MM, color='red', linestyle='dotted', linewidth=2)  # Add dotted red line
    ax1.set_ylabel("Rain amount (mm)")
    ax1.set_title("Forecast Maximum Rainfall (Next 7 Days)")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%a %d %b'))

    # Third subplot: Rain Chance
    ax2.bar(df_latest["date_forecast_applies_to"], df_latest["rain_chance"], color='lightsteelblue')
    ax2.set_ylabel("Rain chance (%)")
    ax2.set_ylim(0, 1)  # Fix y-axis between 0 and 1
    ax2.set_title("Forecast Likelihood of Any Rain (Next 7 Days)")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%a %d %b'))
    ax2.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    # Adjust layout and save image
    plt.tight_layout()

    # Save or show the plot
    if save_file:
        plt.savefig(image_path, dpi=300)
        plt.close()
        logger.info(f"Forecast plot saved as {image_path}")
        return image_path
    else:
        plt.show()

if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    #plot_forecast(file_name="forecast.png")
    plot_forecast(save_file=False)