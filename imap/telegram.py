#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 01:40:15 2021

@author: admin@devops.kiev.ua
"""
import os
import asyncio
import logging

import filetype
from aiogram import Bot, types
from aiogram import exceptions
from configs import settings

ATTACH = settings.TELEGRAM_ATTACH

bot = Bot(token=settings.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
log = logging.getLogger(__name__)

TEMPLATE = """
<b>New email from</b>: {From}
<i>Date</i>: {Date}
<i>Subject:</i> {Subject}
<pre>{Body}</pre>
"""

def is_file_send_photo(file):
    available_type = {'image', 'jpeg', 'pdf'}
    file = filetype.guess(file)
    if file is None:
        return False
    if available_type.intersection(set(file.mime.split("/"))):
        return True
    return False


async def send_message(user_id: int, msg: dict,
                       disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    msg['Body'] = msg['Body'][0:4000] #  limit of telegram message
    try:
        if not ATTACH:
            await bot.send_message(user_id, TEMPLATE.format(**msg),
                                   parse_mode=types.ParseMode.HTML)
        for attachment in msg['Attachments']:
            if is_file_send_photo(attachment['content']):
                await bot.send_photo(user_id, attachment['content'],
                                     caption=ATTACH and msg['Body'] or None)
            else:
                await bot.send_document(user_id, attachment['content'])

    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, msg)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def sender(msg) -> int:
    """
    Simple broadcaster

    :return: Count of messages
    """
    count = 0
    try:
        for user_id in settings.TELEGRAM_USER_IDS:
            if await send_message(user_id, msg):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")
    return count