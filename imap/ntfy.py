#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 21:52:43 2023

@author: goodman@devops.kyiv.ua
"""

import logging
import aiohttp
from configs import settings


log = logging.getLogger(__name__)

async def sender(msg):
    data = msg["Body"]
    title = msg["Subject"]
    file = msg["Attachments"] and msg["Attachments"][0].get("content")
    return await send(settings.NTFY_URL, token=settings.NTFY_TOKEN,
                      tags=settings.NTFY_TAGS, priority=settings.NTFY_PRIORITY,
                      timeout=5, title=title, file=file, msg=data)


async def send(url: str,
               token=None,
               title: str = "New massage",
               tags: str = "slightly_smiling_face",
               msg: str = "",
               markdown="no",
               cache="yes",
               file=None,
               priority: str = "default",
               timeout=10):
    tmout = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=tmout) as session:
        headers = {"Title": title,
                   "Tags": tags,
                   "Priority": priority,
                   "Markdown": markdown,
                   "Cache": cache,
                   "Authorization": f"Bearer {token}"
                   }
        if file:
            headers["Filename"] = "camera.jpg"

        async with session.post(url, headers=headers, data=file or msg) as resp:
            log.info("Sent message to %s, return code %s", url, resp.status)