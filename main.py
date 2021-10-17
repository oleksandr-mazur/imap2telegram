#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 20:30:39 2021

@author: admin@devops.kiev.ua
"""
import os
import aioimaplib
import asyncio
import logging

from parser import get_new_email_id, get_and_parse_email

IMAP_HOST = os.environ["IMAP_HOST"]
IMAP_USER = os.environ["IMAP_USER"]
IMAP_PASSWORD = os.environ["IMAP_PASSWORD"]

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def wait_for_new_message(host: str, user: str, password: str) -> None:
    log.info("Connecting to %s", IMAP_HOST)
    imap_client = aioimaplib.IMAP4_SSL(host=host)
    await imap_client.wait_hello_from_server()

    await imap_client.login(user, password)
    await imap_client.select()

    idle = await imap_client.idle_start(timeout=10)
    while imap_client.has_pending_idle():
        msg = await imap_client.wait_server_push()
        if (email_id := get_new_email_id(msg)) is not None:
            await asyncio.create_task(
                get_and_parse_email(host,
                                    user,
                                    password,
                                    email_id))
        if msg == "DONE":
            imap_client.idle_done()
            await asyncio.wait_for(idle, 1)

    await imap_client.logout()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_for_new_message(IMAP_HOST, IMAP_USER,
                                                 IMAP_PASSWORD))
