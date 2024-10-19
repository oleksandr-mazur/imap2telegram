#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import email
import base64
import asyncio
import logging
import chardet
import random
import aioimaplib

from sender import telegram
from sender import ntfy
from configs import settings

from email.header import decode_header, make_header


log = logging.getLogger(__name__)


def body_decode(message) -> str:
    """Do not fall if cannot decode message."""
    if isinstance(message, str):
        message = message.encode()

    if not isinstance(message, bytes):
        log.warning("Message has unsuported format")
        return str(message)

    coding = chardet.detect(message).get('encoding') or 'utf-8'

    try:
        message = message.decode(coding)
    except Exception as error:
        log.error(error)
        log.error("cannot decode message %s, message type is %s",
                  message, type(message))

    if len(message.strip()) % 4 == 0:
        try:
            message = base64.decodebytes(message)
        except Exception:
            pass

    return str(message)


def parse_header(data):
    """Parse header."""
    return str(make_header(decode_header(data)))


def parse_user_mail(addr, only_mail=False):
    """Parse user and email."""
    alias, mail = email.utils.parseaddr(addr)
    if only_mail:
        return mail
    return (mail, parse_header(alias))


def parse_email(email_obj: email.message) -> dict:
    """Parse email object return json in byte code."""
    body = ""
    attachments = []
    if email_obj.is_multipart():
        for part in email_obj.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # Collecting any files
            if (filename := part.get_filename()):
                attachments.append(
                    {"original_file_name": filename,
                     "content": part.get_payload(decode=True)})
            # Get body
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)
    else:
        body = email_obj.get_payload(decode=True)

    mail, alias = parse_user_mail(email_obj['From'])
    log.info("Got new message from %s <%s>", alias, mail)
    return {
        'From': mail,
        'Alias': alias,
        'To': parse_user_mail(email_obj['To'], only_mail=True),
        'Date': str(email_obj['Date']),
        'Subject': parse_header(email_obj['Subject']),
        'Body': body_decode(body),
        'Attachments': attachments}


async def get_and_parse_email(host: str, user: str, password: str,
                              email_id: int):
    """Get message from server and pass to processing."""
    client = aioimaplib.IMAP4_SSL(host=host)
    await client.wait_hello_from_server()

    await client.login(user, password)
    await client.select(mailbox='INBOX')

    _, data = await client.fetch(email_id, '(RFC822)')
    if len(data) > 1:
        email_task = asyncio.to_thread(email.message_from_bytes, data[1])
        email_message = await asyncio.create_task(email_task)

        parse_task = asyncio.to_thread(parse_email, email_message)
        msg = await asyncio.create_task(parse_task)

        await ntfy.sender(msg)
        await telegram.sender(msg)
    else:
        log.error(data)
    await client.logout()
