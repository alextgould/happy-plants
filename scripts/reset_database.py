
"""
This script resets the database, removing all the data in the tables, so be careful about using this!
"""

import logging
logging.basicConfig(level=logging.DEBUG)

import database

def main():
    db = database.RainfallDatabase()
    db.create_forecast_table(reset=True)
    db.create_historical_table(reset=True)
    db.create_preds_table(reset=True)
    db.check_tables()

if __name__ == "__main__":
    main()