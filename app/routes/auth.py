from flask import request, render_template, redirect, url_for, jsonify, flash, session
from flask_login import login_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app import db
import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
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
            
            # JSONレスポンスの場合
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
            
            # 通常のリクエストの場合は直接リダイレクト
            return redirect(url_for('main.dashboard'))
        else:
            # ログイン失敗
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'メールアドレスまたはパスワードが正しくありません。'})
            
            flash('メールアドレスまたはパスワードが正しくありません。', 'error')
            
    # GETリクエスト時はログインページを表示
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # フォームデータの取得
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # 基本的なバリデーション
            if not email or not password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'すべての必須フィールドを入力してください。'})
                flash('すべての必須フィールドを入力してください。', 'error')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'パスワードが一致しません。'})
                flash('パスワードが一致しません。', 'error')
                return render_template('auth/register.html')
            
            # 既存ユーザーチェック
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'このメールアドレスは既に登録されています。'})
                flash('このメールアドレスは既に登録されています。', 'error')
                return render_template('auth/register.html')
            
            # パスワードハッシュ化
            password_hash = generate_password_hash(password)
            
            # 新規ユーザー作成
            new_user = User(
                email=email,
                password_hash=password_hash,
                created_at=datetime.datetime.now()
            )
            
            # データベースに保存
            db.session.add(new_user)
            db.session.commit()
            
            # ユーザーを自動的にログイン
            login_user(new_user)
            
            # セッションを明示的に保存
            session.permanent = True
            
            # 成功レスポンス
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
            
            # 通常のリクエストの場合はリダイレクト
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            # エラー発生時はログに記録
            app.logger.error(f"Registration error: {str(e)}")
            db.session.rollback()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '登録中にエラーが発生しました。', 'details': str(e)})
            
            flash('登録中にエラーが発生しました。', 'error')
    
    # GETリクエストの場合は登録ページを表示
    return render_template('auth/register.html') 