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
    email_from = msg["From"]

    if not settings.SEND_ONLY_ATTACHMENT:
        await send(settings.NTFY_URL, token=settings.NTFY_TOKEN,
                   tags=settings.NTFY_TAGS, priority=settings.NTFY_PRIORITY,
                   timeout=5, title=title, msg=str(body),
                   markdown=settings.NTFY_MARKDOWN, content_type="text/plain",
                   email_from=email_from)

    for attachment in msg["Attachments"]:
        await send(settings.NTFY_URL, token=settings.NTFY_TOKEN,
                   tags=settings.NTFY_TAGS, priority=settings.NTFY_PRIORITY,
                   timeout=5, title=title, file=attachment["content"],
                   filename=attachment["original_file_name"], msg=body,
                   markdown=settings.NTFY_MARKDOWN, email_from=email_from)


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
               email_from: str = "",
               content_type="text/plain"):
    """Send message to ntfy."""
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
            if r.status == 200:
                log.info("Send email from <{0}> to ntfy topic <{1}>".format(
                    email_from, settings.NTFY_TOPIC))
            else:
                log.error("Fail send email from <{0}> to ntfy topic <{1}>,"
                          " status code {2}".format(
                              email_from, settings.NTFY_TOPIC, r.status))
