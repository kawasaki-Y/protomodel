from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app.routes.account_settings import account_settings_bp
from app.models.models import db

# 損益計算書科目設定ページ
@account_settings_bp.route('/pl', methods=['GET'])
@login_required
def pl_accounts():
    return render_template('account_settings/pl_accounts.html', title='損益計算書科目設定')

# 貸借対照表科目設定ページ
@account_settings_bp.route('/bs', methods=['GET'])
@login_required
def bs_accounts():
    return render_template('account_settings/bs_accounts.html', title='貸借対照表科目設定')

# 資金繰り用科目設定ページ
@account_settings_bp.route('/cf', methods=['GET'])
@login_required
def cf_accounts():
    return render_template('account_settings/cf_accounts.html', title='資金繰り用科目設定')

# 資本政策科目設定ページ
@account_settings_bp.route('/capital', methods=['GET'])
@login_required
def capital_accounts():
    return render_template('account_settings/capital_accounts.html', title='資本政策科目設定') 