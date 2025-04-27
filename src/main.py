import asyncio
import re
import time
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

url = args.website_url
long_sleep = args.long_sleep
short_sleep = args.short_sleep
repetitions = args.repetitions

summary = {}


def createLogString(report: StatusReport):
    if report.remainingPings != -1:
        return f'[{report.url}] [{report.status}] [{report.remainingPings}|{report.totalPings}]'
    return f'[{report.url}] [{report.status}]'


def logInfo(report: StatusReport):
    if (report.status == '200'):
        logger.info(createLogString(report))
    else:
        logger.warning(createLogString(report))


def updateSummary_perfectionist(report: StatusReport):
    try:
        # If we get 2 same consecutive statuses, we save the time, else we ignore the time
        if (summary[report.url]["previousTimeout"] == report.nextTimeout):
            summary[report.url][str(report.status)
                                ]["duration"] += report.nextTimeout
        else:
            summary[report.url]["previousTimeout"] = report.nextTimeout
        summary[report.url][str(report.status)]["iterations"] += 1
    except KeyError:
        # First iteration
        summary[report.url] = {}
        summary[report.url][str(report.status)] = {}
        summary[report.url][str(report.status)]["duration"] = 0
        summary[report.url]["previousTimeout"] = report.nextTimeout
        summary[report.url][str(report.status)]["iterations"] = 1
    return


def updateSummary_badBias(report: StatusReport):
    return


def updateSummary_mixedBias(report: StatusReport):
    return


def updateSummary_goodBias(report: StatusReport):
    return


def updateSummary(report: StatusReport):
    try:

        summary[report.url][str(report.status)] += 1
        summary[report.url][str(report.status)
                            ]["duration"] += report.nextTimeout
        summary[report.url]["lastStatus"] = report.status
    except KeyError:
        # First iteration
        summary[report.url] = {}
        summary[report.url][str(report.status)] = 1


def is_valid_url(url):
    # Simple regex for URL validation
    return re.match(r'^https?:\/\/\S+\.\S+', url) is not None


def validate_arguments(arguments, lineNumber):
    # Check if URL is valid
    if len(arguments) < 1 or not is_valid_url(arguments[0]):
        logger.error(f"Invalid or missing urla pattern on line {lineNumber}")
        return False

    if len(arguments) > 1 and len(arguments) < 3:
        try:
            int(arguments[1])
            int(arguments[2])
        except (ValueError, IndexError):
            logger.error(
                f"Invalid argument types for short and long time on line {lineNumber}")
            return False

    if len(arguments) > 3:
        try:
            int(arguments[3])
        except ValueError:
            logger.error(f"Invalid argument repetitions type on {lineNumber}")
            return False

    return True


async def main():
    global short_sleep
    global long_sleep
    global repetitions
    subscribe_to_status_updates(logInfo)
    subscribe_to_status_updates(updateSummary_perfectionist)

    async with asyncio.TaskGroup() as tg:
        if not sys.stdin.isatty():
            lineCount = 0
            for line in sys.stdin:
                lineCount += 1
                _arguments = line.split()

                if not validate_arguments(_arguments, lineCount):
                    continue

                url = _arguments[0]
                short_sleep = _arguments[1] if 1 < len(
                    _arguments) else short_sleep
                long_sleep = _arguments[2] if 2 < len(
                    _arguments) else long_sleep
                reps = _arguments[3] if 3 < len(_arguments) else repetitions
                tg.create_task(start_website_checker(
                    url,
                    short_sleep,
                    long_sleep,
                    reps
                ))
        elif (args.gui):
            tg.create_task(startupGUI())

    if sys.stdin.isatty():
        tg.create_task(start_website_checker(
            url, short_sleep, long_sleep, reps))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info(summary)
        logger.error(f'{prog_name} force ended')
        try:
            sys.exit(130)
        except SystemExit:
            os
