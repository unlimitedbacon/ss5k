from flask import render_template, url_for
from flask_mail import Message
from app import mail

def send_confirmation(user):
    msg = Message('Jalopalert account confirmation')
    msg.recipients = [user.email]
    msg.body = render_template('emails/confirmation.txt', user=user)
    msg.html = render_template('emails/confirmation.html', user=user)
    mail.send(msg)
