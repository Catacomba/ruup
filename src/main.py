import asyncio
import re
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
from dataclasses import dataclass

_url = args.website_url
_long_sleep = args.long_sleep
_short_sleep = args.short_sleep
_repetitions = args.repetitions
_status_priority = args.status_priority

summary = {}


@dataclass
class StatusSummary:
    totalDuration: int  # in seconds
    occurences: int

    def __iadd(self, other):
        if (isinstance(other, StatusSummary)):
            self.totalDuration += other.totalDuration
            self.occurences += other.occurences


def createLogString(report: StatusReport):
    if report.remainingPings != -1:
        return f'[{report.url}] [{report.status}] [{report.remainingPings}|{report.totalPings}]'
    return f'[{report.url}] [{report.status}]'


def logInfo(report: StatusReport):
    if (report.status == '200'):
        logger.info(createLogString(report))
    else:
        logger.warning(createLogString(report))


def updateSummaryKey_safe(url: str, newStatus: str, nextTimeout: int):
    global summary
    incrementOccurence(url, newStatus)
    if (summary[f'{url}']['lastStatus'] == newStatus):
        # If status is same, we can be confiedent that the status didnt change and duration is valid
        addDuration(url, newStatus)
    else:
        # Since status changed, we are unsure when it did so, so we dont assign durations to noone
        updateUrlData(newStatus, nextTimeout, url)


def updateSummaryKey_unsafe(url: str, newStatus: str, nextTimeout: int):
    global summary
    global status_priority
    incrementOccurence(url, newStatus)
    if (summary[f'{url}']['lastStatus'] == newStatus):
        addDuration(url, newStatus)
    else:
        if (status_priority):
            # new status owns the duration
            addDuration(url, newStatus)
        else:
            # old status owns the duration
            addDuration(url, summary['lastStatus'])
        updateUrlData(newStatus, nextTimeout, url)


def addDuration(url: str, status: str):
    global summary
    summary[f'{url}|{
        status}']['totalDuration'] += summary[f'{url}']['previousDuration']


def incrementOccurence(url: str, newStatus: str):
    global summary
    summary[f'{url}|{newStatus}']['occurences'] += 1
    logger.debug(f'{url}|{newStatus} occurences added, current occurences: {
                 summary[f'{url}|{newStatus}']['occurences']}')


def updateUrlData(newStatus: str, nextTimeout: int, url: str):
    global summary
    summary[f'{url}']['lastStatus'] = newStatus
    summary[f'{url}']['previousDuration'] = nextTimeout


def insertNewSummaryKey(url: str, status: str, duration: int):
    global summary
    summary[f'{url}|{status}'] = {}
    summary[f'{url}|{status}']['totalDuration'] = 0
    summary[f'{url}|{status}']['occurences'] = 0
    summary[f'{url}'] = {}
    summary[f'{url}']['previousDuration'] = duration
    summary[f'{url}']['lastStatus'] = status


def safeSummaryUpdate(report: StatusReport):
    try:
        updateSummaryKey_safe(report.url, report.status, report.nextTimeout)
    except KeyError as ke:
        logger.error(ke)
        insertNewSummaryKey(report.url, report.status, report.nextTimeout)
    return


def unsafeSummaryUpdate(report: StatusReport):
    try:
        updateSummaryKey_unsafe(report.url, report.status, report.nextTimeout)
    except KeyError:
        insertNewSummaryKey(report.url, report.status, report.nextTimeout)
    return


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
    global _short_sleep
    global _long_sleep
    global _repetitions
    subscribe_to_status_updates(logInfo)
    subscribe_to_status_updates(safeSummaryUpdate)

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
                    _arguments) else _short_sleep
                long_sleep = _arguments[2] if 2 < len(
                    _arguments) else _long_sleep
                reps = _arguments[3] if 3 < len(_arguments) else _repetitions
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
            _url, _short_sleep, _long_sleep, _repetitions))

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
