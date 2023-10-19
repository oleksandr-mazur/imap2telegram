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


async def sender(msg: dict) -> None:

    # Each message can be up to 4,096 bytes long.
    # Longer messages are treated as attachments.
    body = msg["Body"].encode()[:4000].decode()
    title = msg["Subject"]

    await send(settings.NTFY_URL, token=settings.NTFY_TOKEN,
               tags=settings.NTFY_TAGS, priority=settings.NTFY_PRIORITY,
               timeout=5, title=title, msg=str(body),
               markdown=settings.NTFY_MARKDOWN, content_type="text/plain")

    for attachment in msg["Attachments"]:
        await send(settings.NTFY_URL, token=settings.NTFY_TOKEN,
                   tags=settings.NTFY_TAGS, priority=settings.NTFY_PRIORITY,
                   timeout=5, title=title, file=attachment["content"],
                   filename=attachment["original_file_name"], msg=body,
                   markdown=settings.NTFY_MARKDOWN)


async def send(url: str,
               token=None,
               title: str = "New massage",
               tags: str = "slightly_smiling_face",
               msg: str = "",
               markdown="no",
               cache="yes",
               file=None,
               filename="default.jpg",
               priority: str = "default",
               timeout=10,
               content_type="text/plain"):
    tmout = aiohttp.ClientTimeout(total=timeout)

    async with aiohttp.ClientSession(timeout=tmout) as session:
        headers = {"Title": title.replace("\n", " ").replace("\r", ""),
                   "Tags": tags,
                   "Priority": priority,
                   "Markdown": markdown,
                   "Cache": cache,
                   "Authorization": f"Bearer {token}",
                   "Content-Type": content_type
                   }
        if file:
            headers["Filename"] = filename

        async with session.post(url, headers=headers, data=file or msg) as r:
            if file:
                log.info("Sent file to %s, return code %s", url, r.status)
            else:
                log.info("Sent message to %s, return code %s", url, r.status)