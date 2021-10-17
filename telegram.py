#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 01:40:15 2021

@author: admin@devops.kiev.ua
"""
import os
import asyncio
import logging

from aiogram import Bot, types
from aiogram.utils import exceptions

API_TOKEN = os.environ["TOKEN"]
USER_IDS = os.environ["USER_IDS"].replace(" ", "").split(",")

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
log = logging.getLogger(__name__)


def get_users():
    """
    Return users list

    In this example returns some random ID's
    """

    yield from USER_IDS


async def send_message(user_id: int, msg: dict, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        for attachment in msg['Attachments']:
            await bot.send_photo(user_id,
                                 attachment['content'],
                                 caption=msg['Date'])

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


async def broadcaster(msg) -> int:
    """
    Simple broadcaster

    :return: Count of messages
    """
    count = 0
    try:
        for user_id in get_users():
            if await send_message(user_id, msg):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")
    return count
