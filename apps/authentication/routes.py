# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for, flash
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass
from apps.authentication.util import confirm_token
from apps.authentication.util import send_verification_email



@blueprint.route('/')
def route_default():
    return redirect(url_for('home_blueprint.student'))



#confirm
@blueprint.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if email is None:
        
        return redirect(url_for('home_blueprint.student'))
    
    user = Users.query.filter_by(email=email).first_or_404()
    if user.is_active:
        flash('Your account is already confirmed.', 'success')
    else:
        user.is_active = True
        db.session.commit()
        print('Your account has been confirmed.', 'success')  
    return redirect(url_for('authentication_blueprint.login'))



# Login & Registration


# @blueprint.route('/login', methods=['GET', 'POST'])
# @limiter.limit("5 per minute")
# def login():
#     login_form = LoginForm(request.form)

#     if request.method == 'POST' and login_form.validate_on_submit():
#         # Baca data form
#         username = login_form.username.data
#         password = login_form.password.data

#         # Cari pengguna berdasarkan username
#         user = Users.query.filter_by(username=username).first()

#         # Verifikasi password
#         if user and verify_pass(password, user.password):
#             login_user(user)  # Login pengguna jika password benar
#             return redirect(url_for('home_blueprint.admin_edit_data_student'))

#          # Jika user sudah terautentikasi, langsung arahkan ke halaman yang diinginkan
#         if current_user.is_authenticated:
#             return redirect(url_for('home_blueprint.admin_edit_data_student'))
        
#         # Jika login gagal (username atau password salah)
#         return render_template(
#             'accounts/login.html',
#             msg='Wrong user or password',
#             form=login_form
#         )
    
       

#     # Jika tidak ada form yang disubmit, tampilkan form login
#     if not current_user.is_authenticated:
#         return render_template('accounts/login.html', form=login_form)

@blueprint.route('/login', methods=['GET', 'POST'])

def login():
    login_form = LoginForm(request.form)

    if request.method == 'POST' and login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data

        # Cari pengguna berdasarkan username
        user = Users.query.filter_by(username=username).first()

        if user:
            # Verifikasi password
            if verify_pass(password, user.password):
                # Periksa apakah email sudah terverifikasi
                if not user.is_active:
                    flash('Please verify your email before logging in.', 'warning')
                    send_verification_email(user)
                    return render_template('accounts/login.html', msg='Email not verified, Check Your Email', form=login_form)

                # Jika email terverifikasi, login pengguna
                login_user(user)
                return redirect(url_for('home_blueprint.admin_edit_data_student'))
            else:
                return render_template('accounts/login.html', msg='Wrong Password or Username', form=login_form)
        else:
            return render_template('accounts/login.html', msg='Wrong Password or Username', form=login_form)

    # Jika user sudah terautentikasi, langsung arahkan ke halaman yang diinginkan
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.admin_edit_data_student'))

    return render_template('accounts/login.html', form=login_form)


# @blueprint.route('/register', methods=['GET', 'POST'])
# def register():
#     create_account_form = CreateAccountForm(request.form)
#     if 'register' in request.form:

#         username = request.form['username']
#         email = request.form['email']

#         # Check usename exists
#         user = Users.query.filter_by(username=username).first()
#         if user:
#             return render_template('accounts/register.html',
#                                    msg='Username already registered',
#                                    success=False,
#                                    form=create_account_form)

#         # Check email exists
#         user = Users.query.filter_by(email=email).first()
#         if user:
#             return render_template('accounts/register.html',
#                                    msg='Email already registered',
#                                    success=False,
#                                    form=create_account_form)

#         # else we can create the user
#         user = Users(**request.form)
#         db.session.add(user)
#         db.session.commit()

#         # Delete user from session
#         logout_user()
        
#         return render_template('accounts/register.html',
#                                msg='User created successfully.',
#                                success=True,
#                                form=create_account_form)

#     else:
#         return render_template('accounts/register.html', form=create_account_form)

# @blueprint.route('/register', methods=['GET', 'POST'])
# def register():
#     create_account_form = CreateAccountForm(request.form)
#     if 'register' in request.form:
#         username = request.form['username']
#         email = request.form['email']

#         # Cek apakah username sudah terdaftar
#         user = Users.query.filter_by(username=username).first()
#         if user:
#             return render_template('accounts/register.html',
#                                     msg='Username already registered',
#                                     success=False,
#                                     form=create_account_form)

#         # Cek apakah email sudah terdaftar
#         user = Users.query.filter_by(email=email).first()
#         if user:
#             return render_template('accounts/register.html',
#                                     msg='Email already registered',
#                                     success=False,
#                                     form=create_account_form)

#         # Buat akun baru
#         user = Users(**request.form)
#         db.session.add(user)
#         db.session.commit()

#         # Kirimkan email verifikasi
#         send_verification_email(user)
        
#         # Logout user otomatis jika sudah terdaftar
#         logout_user()

#         return render_template('accounts/register.html',
#                                 msg='User created successfully. Please check your email to verify your account.',
#                                 success=True,
#                                 form=create_account_form)

#     return render_template('accounts/register.html', form=create_account_form)   


@blueprint.route('/logout')
def logout():
    current_user.is_active = False
    db.session.commit() 
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500




