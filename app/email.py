import smtplib
from email.mime.text import MIMEText

from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject,
                sender, recipients,
                text_body, html_body,
                attachments=None,
                sync=False):

    # MAILTRAP CONFIG
    # port = 2525
    # smtp_server = 'smtp.mailtrap.io'
    # login = '3c7e5f92bcfd6c'
    # password = 'd5926c044d6232'
    # message = ??? # f'string
    # msg = MIMEText(message, 'html')
    # msg['Subject'] = 'Lexus Feedback'
    # msg['From'] = sender
    # msg['To'] = recipients

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body

    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
        # with smtplib.SMTP(smtp_server, port) as server:
        #     server.login(login, password)
        #     server.sendmail(sender, recipients, msg.as_string())
    else:
        Thread(target=send_async_email,
            args=(current_app._get_current_object(), msg)).start()