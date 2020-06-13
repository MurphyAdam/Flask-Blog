from ..email import send_email
from flask import url_for, render_template, current_app

def verify_email(user):
    token = user.generate_confirmation_token()
    link = url_for('auth.confirm_email', token=token, _external=True)
    send_email(('[Lang and Code] Verify your account'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email_confirmationemail.txt',
                                         user=user, link=link),
               html_body=render_template('auth/email_confirmationemail.html',
                                         user=user, link=link))
    print('Email sent 1')


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    link = url_for('auth.reset_password', token=token, _external=True)
    print(link)
    send_email(('[Lang and Code] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, link=link),
               html_body=render_template('email/reset_password.html',
                                         user=user, link=link))
