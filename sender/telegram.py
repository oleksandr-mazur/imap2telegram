#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 01:40:15 2021

@author: admin@devops.kiev.ua
"""
import asyncio
import logging

import filetype
from aiogram import Bot
from aiogram import exceptions
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BufferedInputFile
from aiogram.enums import ParseMode
from configs import settings

log = logging.getLogger(__name__)

bot = Bot(token=settings.TELEGRAM_TOKEN,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))


TEMPLATE = """
<b>New email from</b>: {From}
<i>Date</i>: {Date}
<i>Subject:</i> {Subject}
<pre>{Body}</pre>
"""


def is_file_send_photo(file):
    """Check file type."""
    available_type = {'image', 'jpeg', 'pdf'}
    file = filetype.guess(file)
    if file is None:
        return False
    if available_type.intersection(set(file.mime.split("/"))):
        return True
    return False


async def send_message(user_id: int, msg: dict,
                       disable_notification: bool = False) -> bool:
    """Safe messages sender.

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    msg['Body'] = msg['Body'][0:4096]  # limit of telegram message
    try:
        file = None
        for attachment in msg['Attachments']:
            file = BufferedInputFile(
                file=attachment['content'],
                filename=attachment['original_file_name'])

            if is_file_send_photo(attachment['content']):
                await bot.send_photo(user_id, file,
                                     caption=msg['Body'][0:1024])
            else:
                await bot.send_document(user_id, file)

        if file is None:
            await bot.send_message(user_id, TEMPLATE.format(**msg),
                                   parse_mode=ParseMode.HTML)

    except exceptions.TelegramForbiddenError:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.TelegramNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.TelegramRetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, msg)  # Recursive call
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    except exceptions.AiogramError:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    else:
        log.info("Send email from <{0}> to telegram id {1}".format(
            msg['From'], user_id))
        return True
    return False


async def sender(msg) -> int:
    """Send message to telegram ids sets in TELEGRAM_USER_IDS."""
    for user_id in settings.TELEGRAM_USER_IDS:
        await send_message(user_id, msg)
        # 20 messages per second (Limit: 30 messages per second)
        await asyncio.sleep(.05)
