from dotenv import load_dotenv

import smtplib, ssl
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import email

import imaplib
import re
import os
import time

smtp_ssl_port = 465
DOWNLOAD_DIR = './downloads'

def send_email(receiver, text, files=None):
    with smtplib.SMTP_SSL(hostname, 465) as server:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiver
        msg['Subject'] = 'Holland Foodz EDI test'
        msg.attach(MIMEText(text))

        for f in files or []:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(f, 'rb').read())
            encoders.encode_base64(part)
            filename = os.path.basename(f)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
            msg.attach(part)

        print('Attachments: {}'.format(len(files)))
        server.login(username, password)
        server.ehlo()
        server.sendmail(username, receiver, msg.as_string())
    server.close()

def check_new_mail():
    server = imaplib.IMAP4_SSL(hostname)
    server.login(username, password)

    server.select("Inbox", readonly=False)
    (retcode, messages) = server.search(None, '(UNSEEN)')
    print('Num messages: {}'.format(len(messages[0])))
    if retcode == 'OK':
        for num in messages[0].split():
            typ, data = server.fetch(num,'(RFC822)')
            send_mail = True
            files = []
            for response_part in data:
                if isinstance(response_part, tuple):
                    print('______')
                    mail = email.message_from_bytes(response_part[1])
                    server.store(num, '+FLAGS', '\Seen')

                    print(mail['To'])
                    to_address = mail['To'][mail['To'].find("<")+1:mail['To'].find(">")]
                    print(username, to_address)

                    if username == to_address:
                        print('Error: recipient the same as to address')
                        send_mail = False
                    else:
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

                if send_mail:
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
        check_new_mail()
        time.sleep(10)