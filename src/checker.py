import requests
import datetime
import asyncio
from logger import logger
from arguments import args

from dataclasses import dataclass
from colors import statusColors

long_sleep = args.long_sleep
short_sleep = args.short_sleep
url = args.website_url


@dataclass
class StatusReport:
    status: str
    timeout: int
    checkedDateTime: datetime
    displayStyle: str


subscribers = []


def subscribe_to_status_updates(method):
    subscribers.append(method)


def unsubscribe(method):
    try:
        subscribers.remove(method)
    except ValueError:
        pass


def update_status(report):
    for subscriber in subscribers:
        subscriber(report)


async def start_website_checker():
    while True:
        report = check_website_status(url, short_sleep, long_sleep)
        update_status(report)
        if (report.status == '200'):
            await asyncio.sleep(long_sleep)
        else:
            await asyncio.sleep(short_sleep)


def check_website_status(url, short_sleep, long_sleep) -> StatusReport:
    global sleeptime
    try:
        response = requests.head(url)
        if (response.status_code == 200):
            report = StatusReport(
                status=str(response.status_code),
                timeout=long_sleep,
                checkedDateTime=datetime.datetime.now(),
                displayStyle=statusColors.good_status)
        else:
            report = StatusReport(
                status=str(response.status_code),
                timeout=short_sleep,
                checkedDateTime=datetime.datetime.now(),
                displayStyle=statusColors.bad_status)
        return report
    except requests.RequestException as e:
        logger.error(f'{url} Exception {e}')
        report = StatusReport(
            status='',
            timeout=short_sleep,
            checkedDateTime=datetime.datetime.now(),
            displayStyle=statusColors.unknown_status
        )
        return report
