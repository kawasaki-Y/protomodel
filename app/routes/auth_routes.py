from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン画面と処理"""
    # すでにログインしている場合はダッシュボードにリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # POST処理（ログイン処理）
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        # ユーザー認証
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('ログインに成功しました', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('ユーザー名またはパスワードが正しくありません', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """ログアウト処理"""
    logout_user()
    flash('ログアウトしました', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """ユーザー登録画面と処理"""
    # すでにログインしている場合はダッシュボードにリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # POST処理（ユーザー登録処理）
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # ユーザー名かEメールがすでに使われていないか確認
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('そのユーザー名またはメールアドレスはすでに使用されています', 'danger')
        elif password != password_confirm:
            flash('パスワードが一致しません', 'danger')
        else:
            # 新規ユーザー作成
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            # データベースに保存
            db.session.add(new_user)
            db.session.commit()
            
            # 登録後、自動ログイン
            login_user(new_user)
            flash('アカウントが作成されました！', 'success')
            return redirect(url_for('main.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    """ユーザープロフィール画面"""
    return render_template('auth/profile.html') 