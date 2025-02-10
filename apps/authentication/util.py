# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import hashlib
import binascii

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/


def hash_pass(password):
    """Hash a password for storing."""

    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash)  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""

    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password





from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app, url_for, render_template
from apps import mail
from datetime import datetime, timedelta

def send_verification_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for('authentication_blueprint.confirm_email', token=token, _external=True)
    html = render_template('accounts/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    msg = Message(subject=subject, recipients=[user.email], html=html)
    mail.send(msg)

def generate_confirmation_token(email):
    serializer = Serializer(current_app.config['SECRET_KEY'])
    expires_at = (datetime.utcnow() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')  # Kedaluwarsa 1 jam
    return serializer.dumps({'confirm': email, 'expires_at': expires_at})  # menambahkan salt sebagai tambahan keamanan



def confirm_token(token):
    serializer = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token)
        expires_at = datetime.strptime(data.get('expires_at'), '%Y-%m-%d %H:%M:%S')
        if datetime.utcnow() > expires_at:
            return None  # Token telah kedaluwarsa
        return data.get('confirm')
    except Exception as e:
        return None