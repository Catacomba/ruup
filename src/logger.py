import logging
import os

from logging.handlers import TimedRotatingFileHandler
from rich.logging import RichHandler
from config import prog_name
from arguments import args

url = args.website_url

logger = logging.getLogger(__name__)

# Ensure the logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Define log file path
logname = os.path.join(log_dir, prog_name)

shell_handler = RichHandler()
file_handler = TimedRotatingFileHandler(
    logname, when="midnight", backupCount=30)
file_handler.suffix = '%Y%m%d_%H:%M.log'

logger.setLevel(logging.DEBUG)
shell_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# the formatter determines what our logs will look like
fmt_shell = '%(message)s'
fmt_file = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'

shell_formatter = logging.Formatter(fmt_shell)
file_formatter = logging.Formatter(fmt_file)

# here we hook everything together
shell_handler.setFormatter(shell_formatter)
file_handler.setFormatter(file_formatter)

logger.addHandler(shell_handler)
logger.addHandler(file_handler)

logger.info("Writing logs into: "+file_handler.baseFilename)
