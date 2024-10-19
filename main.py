#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 20:30:39 2021

@author: goodman@devops.kyiv.ua
"""

import sys
import logging
import asyncio
import signal

from imap.base import wait_for_new_message

from configs import settings


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    level=logging.getLevelName(settings.LOG_LEVEL.upper()),
    stream=sys.stdout)


async def shutdown(signal, loop):
    """Cleanup tasks tied to the service's shutdown."""
    logging.info(f"Received exit signal {signal.name}...")

    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

    try:
        [task.cancel() for task in tasks]
        logging.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks)
    except asyncio.exceptions.CancelledError:
        pass
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    try:
        loop.run_until_complete(wait_for_new_message(
            settings.IMAP_HOST,
            settings.IMAP_USER,
            settings.IMAP_PASSWORD
            )
        )
    except asyncio.CancelledError:
        pass
    finally:
        logging.info("Successfully shutdown service")
        loop.close()
