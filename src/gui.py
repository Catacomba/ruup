from arguments import args
from logger import logger
import asyncio

from rich.layout import Layout
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from datetime import datetime

from checker import (
    StatusReport,
    subscribe_to_status_updates,
)
from colors import statusColors


long_sleep = args.long_sleep
short_sleep = args.short_sleep
sleeptime = long_sleep

url = args.website_url
history_size = args.history_size
statusReportHistory = []


async def startupGUI():
    logger.info("Starting GUI task")
    global statusReportHistory
    subscribe_to_status_updates(storeData)
    layout = make_layout()

    with Live(layout, refresh_per_second=60, screen=True):
        while True:
            if len(statusReportHistory) > 0:
                update_current_status(statusReportHistory[0], layout)
            update_status_history(layout, statusReportHistory)
            await asyncio.sleep(0)


def storeData(report: StatusReport):
    global statusReportHistory
    statusReportHistory.insert(0, report)
    if (len(statusReportHistory) > history_size):
        statusReportHistory.pop()


def mockUpdate(counter, layout):
    layout["last_status"].update(Panel(str(counter),
                                       title="Latest Status:",
                                       title_align='left'))


def update_url(url, layout):
    layout["url"].size = len(url)+4
    layout["url"].update(make_url_panel(url))


def update_current_status(status, layout):
    layout["last_status"].update(make_status_panel(status))


def update_status_history(layout, history):
    table = make_history_table()

    for entry in history:
        table.add_row(entry.checkedDateTime.strftime(
            "%Y/%m/%d %H:%M:%S"),
            entry.status,
            style=str(entry.displayStyle.value))

    layout["status_history"].update(table)


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="top_row", size=3),
        Layout(name="status_history"),
    )

    layout["top_row"].split_row(
        Layout(name="url"),
        Layout(name="last_status"),
    )

    layout["url"].update(make_url_panel(url))
    layout["url"].size = len(url)+4
    layout["status_history"].update(make_history_table())
    layout["last_status"].update(make_status_panel(StatusReport(
        status='-1',
        displayStyle=statusColors.unknown_status,
        timeout=0,
        checkedDateTime=datetime.now()
    )))

    return layout


def make_url_panel(url: str) -> Panel:
    return Panel(url,
                 title="Url:",
                 title_align='left',
                 width=len(url)+4)


def make_status_panel(report) -> Panel:
    return Panel(report.status,
                 title="Latest Status:",
                 title_align='left',
                 style=str(report.displayStyle.value),
                 width=len(report.status)+4)


def make_history_table() -> Table:
    table = Table(title="Status history")
    table.add_column("Datetime", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    return table
