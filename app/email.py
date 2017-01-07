from threading import Thread
from flask import render_template, url_for
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_confirmation(user):
    msg = Message('Scrap Scanner 5000 account confirmation')
    msg.recipients = [user.email]
    msg.body = render_template('emails/confirmation.txt', user=user)
    msg.html = render_template('emails/confirmation.html', user=user)
    # We want this to be blocking so that
    # the account will not actually be created
    # if the email doesn't get sent
    #thr = Thread(target=send_async_email, args=[app, msg])
    #thr.start()
    mail.send(msg)

def send_reset(user):
    msg = Message('Scrap Scanner 5000 password reset')
    msg.recipients = [user.email]
    msg.body = render_template('emails/reset-pw.txt', user=user)
    msg.html = render_template('emails/reset-pw.html', user=user)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
