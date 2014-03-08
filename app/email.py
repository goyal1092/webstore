from flask import render_template
from flask.ext.mail import Message
from app import mail
from config import ADMINS

def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)

def signup(user_email):
    send_email('Welcome to Webstore.',
               ADMINS[0],
               user_email,
               render_template('email/signup-email.html')

    )

def order_email(user_email, order, product):
    send_email('Welcome to Webstore.',
               ADMINS[0],
               user_email,
               render_template('email/order-email.html', orderid=order, product=product)

    )

def send_pwd_url(user_email,id):
    send_email('Webstore Admin Request',
               ADMINS[0],
               user_email,
               render_template('email/send-pwd.html', id)
               )