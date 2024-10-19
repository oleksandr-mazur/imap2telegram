#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 07:28:42 2023

@author: goodman@devops.kyiv.ua
"""

from urllib.parse import urlparse

LOG_LEVEL = 'INFO'

SEND_ONLY_ATTACHMENT = False

IMAP_HOST = ""
IMAP_USER = ""
IMAP_PASSWORD = ''

TELEGRAM_USER_IDS = []
TELEGRAM_TOKEN = ""
TELEGRAM_ATTACH = True

NTFY_URL = ""
NTFY_TOKEN = ""
NTFY_TAGS = ""
NTFY_PRIORITY = "default"
NTFY_MARKDOWN = "no"

from configs.settings_local import *

NTFY_TOPIC = urlparse(NTFY_URL).path.strip("/")
