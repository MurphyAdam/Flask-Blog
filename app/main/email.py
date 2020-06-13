from ..email import send_email
from flask import url_for, render_template, current_app



def contact_us_send_email(subject, body, email, fullname):
    send_email(('[Lang and Code] New email'),
               sender=current_app.config['ADMINS'][0],
               recipients=["elm.majidi@gmail.com"],
               text_body=render_template('email/contact_us.txt',
                                         subject=subject, body=body,
                                         email=email, fullname=fullname),
               html_body=render_template('email/contact_us.html',
                                         subject=subject, body=body,
                                         email=email, fullname=fullname))