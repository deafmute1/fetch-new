# stdlib
from pathlib import Path 
import os 
from runpy import run_path
import logging

VALID_CONFIG_VALUES =   ('LOG_LEVEL', 'TRANSFER_TIMEOUT', "SOURCE", 'DESTINATION', 'MODE')
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
TRANSFER_TIMEOUT = int(os.getenv('TRANSFER_TIMEOUT', 15))
SOURCE = os.getenv('SOURCE', '/source')
DESTINATION = os.getenv('DESTINATION', '/destination')
MODE = os.getenv('MODE', 'NEW')

if SOURCE is None or DESTINATION is None: 
    raise ValueError("SOURCE or DESTINATION is None")