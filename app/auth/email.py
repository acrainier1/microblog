import smtplib
from email.mime.text import MIMEText
from flask import render_template, current_app
from flask_babel import _
from app.email import send_email




def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),    # subject
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))
    print('SEND_password_reset_email')


def send_mail(email=''):
    # MAILTRAP CONFIG
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = '3c7e5f92bcfd6c'
    password = 'd5926c044d6232'

    sender = 'kanjiremastered@gmail.com'
    recipient = 'alex.c.canizales@gmail.com'
    message = f"<h2>Stuff about Mailtrap from {sender} to {recipient}</h2>"
    msg = MIMEText(message, 'html')
    msg['Subject'] = 'A Test of Mailtrap.io'
    msg['From'] = sender
    msg['To'] = recipient

    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender, recipient, msg.as_string())