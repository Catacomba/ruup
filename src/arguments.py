import argparse
from config import prog_name

parser = argparse.ArgumentParser(
    prog=prog_name,
    description="r u up? A simple website monitor and status logger",
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
    "-r",
    "--repetitions",
    help="Number of times to perform the online check, default is -1 which also represents infinity",
    default=-1,
    type=int)
parser.add_argument(
    "-g",
    "--gui",
    help="Display the full screen GUI",
    action='store_true')
parser.add_argument(
    "-p",
    "--status-priority",
    default=True,
    help="Defines what to do when adding duration to summary and status differs from previous status. If true add duration to new status, if false add duration to old status",
    type=bool)
parser.add_argument(
    "-hs",
    "--history-size",
    default=20,
    help="Number of lines to display in the GUI history. Default is 20",
    type=int)

args = parser.parse_args()
