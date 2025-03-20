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