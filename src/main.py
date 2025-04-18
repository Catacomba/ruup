import asyncio
import os
import sys
from config import prog_name
from logger import logger
from gui import startupGUI
from arguments import args
from checker import (
    start_website_checker,
    subscribe_to_status_updates,
    StatusReport
)

long_sleep = args.long_sleep
short_sleep = args.short_sleep
sleeptime = long_sleep

url = args.website_url


def createLogString(status: str, url: str):
    return f'[{url}] status: [{status}]'


def logInfo(report: StatusReport):
    if (report.status == '200'):
        logger.info(createLogString(report.status, url))
    else:
        logger.warning(createLogString(report.status, url))


async def main():
    subscribe_to_status_updates(logInfo)
    async with asyncio.TaskGroup() as tg:
        if (args.gui):
            tg.create_task(startupGUI())
        tg.create_task(start_website_checker())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error(f'{prog_name} force ended')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
