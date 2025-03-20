
# In theory, including __init__.py in the src/ folder turns it into a Python package
# This allows you to import functions across different modules using relative imports

# For Python 3.3 onwards this isn't actually needed

# In practice I'm finding even with __init__.py I'm having issues with the scripts folder picking up the src folder contents
# Sometimes it needs to be src.database, other times just database, linter doesn't work without custom .vscode settings etc
