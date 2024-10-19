import os
import sys
import time
import smtplib

from email.message import EmailMessage


email = os.getenv("IMAP_USER")
password = os.getenv("IMAP_PASSWORD")
host = os.getenv("IMAP_HOST")

def sendmessage(count=10):
    server = smtplib.SMTP_SSL(host, 465)
    server.ehlo("hello")
    server.login(email, "GeivrinJetdiackdopt4")
    msg = EmailMessage()
    msg['Subject'] = "Text message"
    msg['From'] = email
    msg['To'] = email
    msg['Body'] = 'This is text email'
    msg.add_header('Content-Type', 'text/plain')
    msg.set_content("""\
    Salut!

    This is test email.
    """)
    for each in range(0, count):
        time.sleep(0.1)
        server.send_message(msg)
        print(f"Sent message number {each}")
    server.quit()


if __name__ == "__main__":
    sendmessage(count=int(sys.argv[1]))
