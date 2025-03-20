from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app import db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('メールアドレスまたはパスワードが正しくありません')
    return render_template('auth/login.html', title='ログイン', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.get_by_email(form.email.data)
        if existing_user:
            flash('このメールアドレスは既に登録されています')
            return render_template('auth/register.html', title='アカウント登録', form=form)
            
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('アカウントが作成されました。ログインしてください。')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='アカウント登録', form=form) 