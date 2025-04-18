import argparse
from config import prog_name

parser = argparse.ArgumentParser(
    prog=prog_name,
    description="A simple website monitor",
    usage='%(prog)s [options]')

parser.add_argument(
    "-w",
    "--website-url",
    help="Url of the website",
    type=str)
parser.add_argument(
    "-l",
    "--long-sleep",
    help="Long sleep time in seconds (used if website is running normally) default is 300 (5 minutes)",
    default=300,
    type=int)
parser.add_argument(
    "-s",
    "--short-sleep",
    help="Short sleep time in seconds (used if website is down), default is 30 seconds",
    default=30,
    type=int)
parser.add_argument(
    "-g",
    "--gui",
    help="Display the full screen GUI",
    action='store_true')
parser.add_argument(
    "-hs",
    "--history_size",
    default=20,
    help="Number of lines to display in the GUI history. Default is 20",
    type=int)

args = parser.parse_args()
