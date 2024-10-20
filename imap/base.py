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


def get_email_id(msg: dict) -> int:
    """Return list with id of new email."""
    try:
        attr = {x.decode().split()[1]: x.decode().split()[0] for x in msg}
        return int(attr["EXISTS"])
    except (AttributeError, KeyError, IndexError):
        return


def unseen_mail(result) -> list:
    """Return unseen email ids."""
    if result.result == "OK":
        return [int(x) for x in result.lines.pop(0).decode().split()]
    return []


def run_handler(host, user, password, email_id):
    task_name = f"email_task-{email_id}"

    tasks = [x.get_name() for x in asyncio.all_tasks()]

    if task_name not in tasks:
        return asyncio.create_task(
            get_and_parse_email(host, user, password, email_id),
            name=task_name)


async def wait_for_new_message(host: str, user: str, password: str) -> None:
    """
    Run imap getting loop.

    Args:
        host (str): imap servet host.
        user (str): imap user.
        password (str): imap password.

    """
    log.info("Connected to %s", host)

    client = aioimaplib.IMAP4_SSL(host=host, timeout=30)
    await client.wait_hello_from_server()

    await client.login(user, password)
    await client.select()

    log.info("Listening email %s", user)

    try:
        while True:
            log.info("Running asyncio tasks: %s",
                     [x.get_name() for x in asyncio.all_tasks()])

            idle = await client.idle_start(timeout=60)
            msg = await client.wait_server_push()
            log.info(f"Data from server: {msg}")

            if email_id := get_email_id(msg):
                log.info(f"Find new email id: {email_id}")
                run_handler(host, user, password, email_id)

            client.idle_done()
            await asyncio.wait_for(idle, 30)

            log.info("Search unseen emails")
            if unseen_ids := unseen_mail(await client.search('UNSEEN')):
                log.info(f"Find unseen emails ids: {unseen_ids}")
                for email_id in unseen_ids:
                    run_handler(host, user, password, email_id)
            else:
                log.info("Unseen emails not found")

    except asyncio.CancelledError:
        logging.info("Send DONE to server... ")
        client.idle_done()
        logging.info("Waiting idle to done")
        await asyncio.wait_for(idle, 1)
        logging.info("Logout form server..")
        await client.logout()
