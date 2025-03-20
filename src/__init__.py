
# In theory, including __init__.py in the src/ folder turns it into a Python package
# This allows you to import functions across different modules using relative imports

# For Python 3.3 onwards this isn't actually needed

# In practice I'm finding even with __init__.py I'm having issues with the scripts folder picking up the src folder contents
# Sometimes it needs to be src.database, other times just database, linter doesn't work without custom .vscode settings etc

# TODO: move this commentary to devlog and delete this file
# along with the add_src_to_path.py script
# (still thinking about this actually - need to test in linux server env where there's no .vscode folder to confirm it works)