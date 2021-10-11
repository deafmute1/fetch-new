# stdlib
from pathlib import Path 
import os 
from runpy import run_path
import logging

VALID_CONFIG_VALUES =   ('LOG_LEVEL', 'TRANSFER_TIMEOUT', "SOURCE", 'DESTINATION', 'MODE')
LOG_LEVEL = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
TRANSFER_TIMEOUT = int(os.getenv('TRANSFER_TIMEOUT', 15))

GID = int(os.getenv('GID', -1))  # in os.chown, -1 leaves id unchanged.
UID = int(os.getenv('UID', -1))

CHMOD= os.getenv('CHOWN')
if CHMOD is not None: 
    CHMOD = oct(int(CHMOD, 8)) # convert a string reprsentation of an octal to a python octal, via a python int in base 8.

SOURCE = os.getenv('SOURCE', '/source')
DESTINATION = os.getenv('DESTINATION', '/destination')
MODE = os.getenv('MODE', 'NEW')

if SOURCE is None or DESTINATION is None: 
    raise ValueError("SOURCE or DESTINATION is None")