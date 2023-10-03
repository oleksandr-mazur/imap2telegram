#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 20:30:39 2021

@author: goodman@devops.kyiv.ua
"""

import sys
import logging
import asyncio

from imap.base import wait_for_new_message


from configs import settings


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    level=logging.getLevelName(settings.LOG_LEVEL.upper()),
    stream=sys.stdout)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_for_new_message(
        settings.IMAP_HOST,
        settings.IMAP_USER,
        settings.IMAP_PASSWORD
        )
    )