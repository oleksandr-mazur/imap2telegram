#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 21:34:52 2023

@author: goodman@devops.kyiv.ua
"""

import logging
import asyncio

import aioimaplib

from imap.parser import get_and_parse_email

log = logging.getLogger(__name__)


def get_email_ids(msg: dict, last_id: int) -> list:
    """Parse and return actual email ids."""
    try:
        attr = {x.decode().split()[1]: x.decode().split()[0] for x in msg}
        exists = int(attr["EXISTS"])
        recent = int(attr["RECENT"])
    except (AttributeError, KeyError, IndexError):
        return []

    # HACK: if server not return all information about massage
    ids = [x for x in range(exists-recent+1, exists+1)]
    if len(ids) == 1:
        return ids
    if last_id != 0:
        return [x for x in ids if x > last_id]
    return ids


async def wait_for_new_message(host: str, user: str, password: str) -> None:
    """
    Run imap getting loop.

    Args:
        host (str): imap servet host.
        user (str): imap user.
        password (str): imap password.

    """
    log.info("Connected to %s", host)

    imap_client = aioimaplib.IMAP4_SSL(host=host)
    await imap_client.wait_hello_from_server()

    await imap_client.login(user, password)
    await imap_client.select()

    log.info("Listening email %s", user)
    last_processed_email_id = 0

    idle = await imap_client.idle_start()

    try:
        while imap_client.has_pending_idle():

            msg = await imap_client.wait_server_push()
            log.info(f"Data from server: {msg}")

            if email_ids := get_email_ids(msg, last_processed_email_id):
                for email_id in email_ids:
                    log.info(f"Start processind task-{email_id}")
                    asyncio.create_task(
                        get_and_parse_email(host, user, password, email_id))
                    last_processed_email_id = email_id
    except asyncio.CancelledError:
        logging.info("Send DONE to server... ")
        imap_client.idle_done()
        logging.info("Waiting idle to done")
        await asyncio.wait_for(idle, 1)
        logging.info("Logout form server..")
        await imap_client.logout()
