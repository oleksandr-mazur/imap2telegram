#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 20:30:39 2021

@author: admin@devops.kiev.ua
"""
import os
import sys
import aioimaplib
import asyncio
import logging

from parser import get_new_email_id, get_and_parse_email

IMAP_HOST = os.environ["IMAP_HOST"]
IMAP_USER = os.environ["IMAP_USER"]
IMAP_PASSWORD = os.environ["IMAP_PASSWORD"]

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    level=logging.getLevelName(LOG_LEVEL),
    stream=sys.stdout)


log = logging.getLogger("main")


async def wait_for_new_message(host: str, user: str, password: str) -> None:
    log.info("Connecting to %s", IMAP_HOST)
    imap_client = aioimaplib.IMAP4_SSL(host=host, timeout=30)
    await imap_client.wait_hello_from_server()

    await imap_client.login(user, password)
    await imap_client.select()

    log.info("Listening email %s", IMAP_USER)

    while True:
        idle = await imap_client.idle_start(timeout=60)
        msg = await imap_client.wait_server_push()
        if email_id := get_new_email_id(msg):
            await asyncio.create_task(
                get_and_parse_email(host, user, password, email_id))
        log.info(msg)

        imap_client.idle_done()
        await asyncio.wait_for(idle, 30)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_for_new_message(IMAP_HOST, IMAP_USER,
                                                 IMAP_PASSWORD))
