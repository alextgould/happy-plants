
import logging
logging.basicConfig(level=logging.DEBUG)

from database import create_forecast_table, create_historical_table, check_tables

def main(print_output=True):

    create_forecast_table(reset=True)
    create_historical_table(reset=True)

    if print_output:
        check_tables()

if __name__ == "__main__":
    main()