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
    url: str
    status: str
    nextTimeout: int
    checkedDateTime: datetime
    displayStyle: str
    remainingPings: int = -1
    totalPings: int = -1


subscribers = []


def subscribe_to_status_updates(method):
    subscribers.append(method)


def unsubscribe(method):
    try:
        subscribers.remove(method)
    except ValueError:
        pass


def publish_status(report):
    for subscriber in subscribers:
        subscriber(report)


async def start_website_checker(
        url: str,
        short_sleep: int,
        long_sleep: int,
        repetitions: int = -1):
    logger.info(f"Starting checker: "
                f"[url: {url}] "
                f"[short sleep: {short_sleep}] "
                f"[long sleep: {long_sleep}] "
                f"[repetitions:{'unlimited' if repetitions == -1 else repetitions}]")
    _counter = int(repetitions)
    _short_sleep = int(short_sleep)
    _long_sleep = int(long_sleep)

    if (_counter == -1):
        report = check_website_status(url, _short_sleep, _long_sleep)
        publish_status(report)
        while True:
            await asyncio.sleep(report.nextTimeout)
            if (report.status == '200'):
                await asyncio.sleep(_long_sleep)
            else:
                await asyncio.sleep(_short_sleep)
            report = check_website_status(url, _short_sleep, _long_sleep)
            publish_status(report)
    else:
        report = check_website_status(
            url, _short_sleep, _long_sleep)
        report.totalPings = _counter
        report.remainingPings = _counter
        publish_status(report)
        for i in range(_counter-1):
            await asyncio.sleep(report.nextTimeout)
            report = check_website_status(
                url, _short_sleep, _long_sleep)
            report.totalPings = _counter
            report.remainingPings = _counter-(i+1)
            publish_status(report)
        logger.info(f"[{url}] finished pinging")


def check_website_status(url, short_sleep, long_sleep) -> StatusReport:
    global sleeptime
    try:
        response = requests.head(url)
        if (response.status_code == 200):
            report = StatusReport(
                url=url,
                status=str(response.status_code),
                nextTimeout=long_sleep,
                checkedDateTime=datetime.datetime.now(),
                displayStyle=statusColors.good_status,
            )
        else:
            report = StatusReport(
                url=url,
                status=str(response.status_code),
                nextTimeout=short_sleep,
                checkedDateTime=datetime.datetime.now(),
                displayStyle=statusColors.bad_status,
            )
        return report
    except requests.RequestException as e:
        logger.error(f'{url} Exception {e}')
        report = StatusReport(
            url=url,
            status='',
            nextTimeout=short_sleep,
            checkedDateTime=datetime.datetime.now(),
            displayStyle=statusColors.unknown_status,
        )
        return report
