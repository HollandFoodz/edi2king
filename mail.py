from dotenv import load_dotenv

import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email


import imaplib
import re
import os
import time

smtp_ssl_port = 465

DOWNLOAD_DIR = './downloads'
list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

def parse_list_response(line):
    print(line)
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    return (flags, delimiter, mailbox_name)



def send_email(receiver, text, files=None):
    with smtplib.SMTP_SSL(hostname, 465) as server:
        server.login(username, password)
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiver
        msg['Subject'] = 'Holland Foodz EDI test'
        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=os.path.basename(f)
                )
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
            msg.attach(part)

        print('Attachments: {}'.format(len(files)))
        server.sendmail(username, receiver, msg.as_string())

def imap():
    server = imaplib.IMAP4_SSL(hostname)
    server.login(username, password)

    server.select("Inbox", readonly=True)
    (retcode, messages) = server.search(None, '(UNSEEN)')
    print('Num messages: {}'.format(len(messages[0])))
    if retcode == 'OK':
        for num in messages[0].split():
            typ, data = server.fetch(num,'(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    print('______')
                    mail = email.message_from_bytes(response_part[1])
                    print(mail['Subject'])
                    files = []
                    for part in mail.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is None:
                            continue

                        file_name = part.get_filename()
                        if file_name:
                            print('Downloading {}'.format(file_name))
                            path = os.path.join(DOWNLOAD_DIR, file_name)
                            fp = open(path, 'wb')
                            fp.write(part.get_payload(decode=True))
                            files.append(path)

                send_email(os.getenv('TEST_RECEIVER_EMAIL'), 'Received EDI order', files=files)
    
    server.logout()


if __name__ == '__main__':
    load_dotenv()

    hostname = os.getenv('HOSTNAME')
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    # send_email(os.getenv('TEST_RECEIVER_EMAIL'), 'Received EDI order', ['downloads/order2.edi'])
    while (True):
        print('Checking e-mail: {}'.format(username))
        imap()
        time.sleep(10)