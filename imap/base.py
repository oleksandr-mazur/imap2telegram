#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 21:34:52 2023

@author: goodman@devops.kyiv.ua
"""

import logging
import asyncio
from configs import settings

import aioimaplib

from imap.parser import get_new_email_id, get_and_parse_email

log = logging.getLogger(__name__)


async def wait_for_new_message(host: str, user: str, password: str) -> None:
    """
    Run imap getting loop.

    Args:
        host (str): imap servet host.
        user (str): imap user.
        password (str): imap password.

    """
    log.info("Connected to %s", host)

    imap_client = aioimaplib.IMAP4_SSL(host=host, timeout=30)

    await imap_client.wait_hello_from_server()
    await imap_client.login(user, password)
    await imap_client.select()

    log.info("Listening email %s", user)

    while True:
        idle = await imap_client.idle_start(timeout=60)
        msg = await imap_client.wait_server_push()

        if email_id := get_new_email_id(msg):
            await asyncio.create_task(
                get_and_parse_email(host, user, password, email_id))
        log.debug(msg)

        imap_client.idle_done()
        await asyncio.wait_for(idle, 30)