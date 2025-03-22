from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from functools import wraps
import secrets
from datetime import datetime, timedelta
from app.forms.auth_forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse
from werkzeug.security import check_password_hash
from flask import session

# Blueprintの定義
bp = Blueprint('auth', __name__, url_prefix='/auth')

# ==========================================================
# 権限管理用のデコレータ
# ==========================================================

# 管理者権限チェック用のデコレータ
# 管理者以外のアクセスを制限する時に使う
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('この操作には管理者権限が必要です', 'danger')
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

# ==========================================================
# 基本的な認証機能
# ==========================================================

# トップページのルーティング
# ログイン済みならnumerical_plan.indexへ、未ログインならログイン画面へ
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

# ログイン機能
# POSTの場合はログイン処理、GETの場合はログイン画面表示
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # ユーザー認証のロジック
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # ログイン成功
            login_user(user, remember=True)
            
            # ここでセッションを明示的に保存
            session.permanent = True
            
            # JSONリクエストの場合は、JSONレスポンスを返す
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
            
            # 通常のフォーム送信の場合は直接リダイレクト
            return redirect(url_for('main.dashboard'))
        else:
            # ログイン失敗
            if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'メールアドレスまたはパスワードが正しくありません。'})
            
            flash('メールアドレスまたはパスワードが正しくありません。', 'error')
            
    # GETリクエスト時はログインページを表示
    return render_template('auth/login.html')

# ==========================================================
# アカウント管理機能
# ==========================================================

# 新規アカウント作成（サインアップ）
@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    新規ユーザー登録
    
    GET: 登録フォームの表示
    POST: ユーザーの新規作成
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        try:
            # ユーザー情報の取得
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # 基本的なバリデーション
            if not email or not password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'メールアドレスとパスワードは必須です。'})
                flash('メールアドレスとパスワードは必須です。', 'error')
                return render_template('auth/signup.html')
            
            # メールアドレスの重複チェック
            if User.query.filter_by(email=email).first():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'このメールアドレスは既に登録されています。'})
                flash('このメールアドレスは既に登録されています。', 'error')
                return render_template('auth/signup.html')
            
            # 新規ユーザーの作成
            user = User(username=username or email.split('@')[0], email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # 登録完了後の自動ログイン
            login_user(user)
            
            # JSONリクエストの場合は、JSONレスポンスを返す
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'redirect': url_for('main.dashboard'),
                    'message': 'アカウントが正常に作成されました。'
                })
            
            # 通常のフォーム送信の場合は直接リダイレクト
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            # エラーをログに記録
            current_app.logger.error(f'Signup error: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '登録中にエラーが発生しました。', 'error': str(e)})
            
            flash('登録中にエラーが発生しました。', 'error')
            
    return render_template('auth/signup.html')

@bp.route('/logout')
@login_required
def logout():
    """ログアウト処理"""
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # メールアドレスの重複チェック
        if User.query.filter_by(email=form.email.data).first():
            flash('このメールアドレスは既に登録されています', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('アカウントが作成されました。ログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(f"Registration error: {e}")  # デバッグ用
            db.session.rollback()
            flash('アカウントの作成に失敗しました。', 'error')
    
    return render_template('auth/register.html', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
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

@bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    """ユーザー管理画面（管理者専用）"""
    users = User.query.all()
    return render_template('auth/manage_users.html', users=users)

@bp.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
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

@bp.route('/admin/users/new', methods=['GET', 'POST'])
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

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
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

# パスワードリセットトークンのモデル追加
class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """トークンが24時間以内か確認"""
        expiration = self.created_at + timedelta(hours=24)
        return datetime.utcnow() <= expiration

# パスワードリセットのルート
@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """パスワード再設定ページを表示します"""
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    reset = PasswordReset.query.filter_by(token=token).first()
    
    if not reset or not reset.is_valid():
        flash('無効または期限切れのトークンです', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('パスワードが一致しません', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        
        user = User.query.filter_by(email=reset.email).first()
        if user:
            user.set_password(password)
            
            # リセットトークンを削除
            PasswordReset.query.filter_by(email=reset.email).delete()
            db.session.commit()
            
            flash('パスワードがリセットされました。新しいパスワードでログインしてください', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('エラーが発生しました', 'error')
    
    return render_template('auth/reset_password.html')

@bp.route('/debug/users')
def debug_users():
    if not app.debug:
        return "Debug mode is disabled", 403
        
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'has_password': bool(user.password_hash)
        })
    return str(result) 