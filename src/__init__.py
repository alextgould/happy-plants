
# Including __init__.py in the src/ folder turns it into a Python package.

# This allows you to import functions across different modules using relative imports.

# For example, without __init__.py, running scripts/collect_data.py might give you an error when trying to import from src.data_ingestion.

# With it, you can do:
# from src.data_ingestion import fetch_rainfall_data
# from src.database import store_data