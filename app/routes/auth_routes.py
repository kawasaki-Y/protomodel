from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# 管理者権限が必要なルート用のデコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('この操作には管理者権限が必要です', 'danger')
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# 特定の権限が必要なルート用のデコレータ
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_permission(permission):
                flash('この操作に必要な権限がありません', 'danger')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """ユーザープロフィール画面と編集"""
    if request.method == 'POST':
        # 現在のパスワード確認（セキュリティのため）
        current_password = request.form.get('current_password')
        if not current_user.check_password(current_password):
            flash('現在のパスワードが正しくありません', 'danger')
            return redirect(url_for('auth.profile'))
        
        # ユーザー情報の更新
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        
        # パスワード変更（入力がある場合のみ）
        new_password = request.form.get('new_password')
        if new_password:
            confirm_password = request.form.get('confirm_password')
            if new_password != confirm_password:
                flash('新しいパスワードが一致しません', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.set_password(new_password)
        
        db.session.commit()
        flash('プロフィールが更新されました', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

@auth_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """ユーザー管理画面（管理者専用）"""
    users = User.query.all()
    return render_template('auth/manage_users.html', users=users)

@auth_bp.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """ユーザー編集画面（管理者専用）"""
    user = User.query.get_or_404(user_id)
    
    # 自分自身は管理画面から編集させない（プロフィール画面で行う）
    if user.id == current_user.id:
        flash('自分自身のアカウントはプロフィール画面から編集してください', 'warning')
        return redirect(url_for('auth.manage_users'))
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        # user.role = request.form.get('role')
        user.is_admin = request.form.get('is_admin') == 'on'
        
        # 権限の更新
        # permissions = {}
        # for perm in ['create_plan', 'edit_plan', 'delete_plan', 'view_all_plans', 'manage_users']:
        #     permissions[perm] = request.form.get(perm) == 'on'
        
        # user.permissions = permissions
        
        # パスワードリセット（入力がある場合のみ）
        new_password = request.form.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash(f'ユーザー {user.username} の情報が更新されました', 'success')
        return redirect(url_for('auth.manage_users'))
    
    return render_template('auth/edit_user.html', user=user)

@auth_bp.route('/admin/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """新規ユーザー作成画面（管理者専用）"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        # role = request.form.get('role')
        is_admin = request.form.get('is_admin') == 'on'
        
        # ユーザー名かEメールがすでに使われていないか確認
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            flash('そのユーザー名またはメールアドレスはすでに使用されています', 'danger')
        else:
            # 権限の設定
            # permissions = {}
            # for perm in ['create_plan', 'edit_plan', 'delete_plan', 'view_all_plans', 'manage_users']:
            #     permissions[perm] = request.form.get(perm) == 'on'
            
            # 新規ユーザー作成
            new_user = User(
                username=username, 
                email=email,
                # role=role,
                is_admin=is_admin,
                # permissions=permissions
            )
            new_user.set_password(password)
            
            # データベースに保存
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'ユーザー {username} が作成されました', 'success')
            return redirect(url_for('auth.manage_users'))
    
    return render_template('auth/create_user.html')

@auth_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """ユーザー削除（管理者専用）"""
    user = User.query.get_or_404(user_id)
    
    # 自分自身は削除できない
    if user.id == current_user.id:
        flash('自分自身のアカウントは削除できません', 'danger')
        return redirect(url_for('auth.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'ユーザー {user.username} が削除されました', 'success')
    return redirect(url_for('auth.manage_users')) 