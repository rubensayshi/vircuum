import logging, sys

# ensure all error traces are send to the logs
logging.basicConfig(stream=sys.stderr)

# import app
from vircu.app import app
