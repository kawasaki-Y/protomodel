from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.revenue_business import RevenueBusiness
from app import db

revenue_model_bp = Blueprint('revenue_model', __name__, url_prefix='/revenue-model')

@revenue_model_bp.route('/wizard')
@login_required
def wizard():
    """
    収益モデル診断ウィザード
    
    Q&A形式でユーザーに複数の質問を投げかけ、
    最適なビジネスモデルを提案する。
    """
    return render_template('revenue_model/wizard.html')

@revenue_model_bp.route('/wizard/submit', methods=['POST'])
@login_required
def wizard_submit():
    """
    ウィザード結果の受け取り・分析
    
    - 質問回答を分析してモデル候補を1つ提案
    - 「次へ進む」ボタン押下で収益モデル作成画面へ移動
    """
    data = request.json
    
    # ここで回答内容を元にモデルを推論するロジックを実装
    # 例: question1 が 'yes' なら単価×数量モデルを提案 など
    # ここでは簡易的に固定で返す
    model_type = "unit_price"
    recommended_name = "単価×販売数モデル"
    
    return jsonify({
        'model_type': model_type,
        'recommended_name': recommended_name
    })

@revenue_model_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    収益モデル作成画面

    - 事業名 / ビジネスモデル種別 / タグなどを入力して保存
    """
    if request.method == 'POST':
        form_data = request.form
        new_business = RevenueBusiness(
            user_id=current_user.id,
            name=form_data['name'],
            model_type=form_data['model_type'],
            description=form_data.get('description', ''),
            tags=form_data.getlist('tags')  # タグの複数入力にも対応可能
        )
        db.session.add(new_business)
        db.session.commit()
        return redirect(url_for('revenue_model.list'))  # 作成後は一覧表示へリダイレクト

    return render_template('revenue_model/create.html')

@revenue_model_bp.route('/list')
@login_required
def list():
    """
    登録済みの収益モデル一覧を表示
    """
    businesses = RevenueBusiness.query.filter_by(user_id=current_user.id).all()
    return render_template('revenue_model/list.html', businesses=businesses) 