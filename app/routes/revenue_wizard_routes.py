from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.models import db, RevenueBusinessModel, RevenueTag, BusinessPlan

revenue_wizard_bp = Blueprint('revenue_wizard', __name__, url_prefix='/revenue-wizard')

# ビジネスモデルの定義
BUSINESS_MODELS = {
    'unit_sales': {
        'name': '従量課金型',
        'description': '商品やサービスの利用量に応じて課金するモデル',
        'parameters': [
            {
                'id': 'unit_price',
                'label': '単価',
                'type': 'number',
                'unit': '円',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'monthly_units',
                'label': '月間予想販売数',
                'type': 'number',
                'required': True,
                'min': 0,
                'step': 1
            }
        ],
        'questions': [
            '商品やサービスの価格は利用量に応じて変動しますか？',
            '顧客は必要な分だけ購入や利用ができますか？',
            '在庫管理や供給能力の調整が必要ですか？'
        ]
    },
    'subscription': {
        'name': 'サブスクリプション型',
        'description': '定期的な料金を支払って継続的にサービスを利用するモデル',
        'parameters': [
            {
                'id': 'monthly_fee',
                'label': '月額料金',
                'type': 'number',
                'unit': '円',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'subscribers',
                'label': '想定契約者数',
                'type': 'number',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'churn_rate',
                'label': '月間解約率',
                'type': 'number',
                'unit': '%',
                'required': True,
                'min': 0,
                'max': 100,
                'step': 0.1
            }
        ],
        'questions': [
            'サービスは継続的に提供されますか？',
            '定期的な収入を見込めますか？',
            '顧客との長期的な関係構築が重要ですか？'
        ]
    },
    'advertising': {
        'name': '広告収入型',
        'description': '広告掲載やスポンサーシップによる収入モデル',
        'parameters': [
            {
                'id': 'monthly_views',
                'label': '月間想定PV数',
                'type': 'number',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'ad_unit_price',
                'label': '広告単価（CPM）',
                'type': 'number',
                'unit': '円',
                'required': True,
                'min': 0,
                'step': 0.1
            }
        ],
        'questions': [
            '大規模なユーザーベースを獲得できますか？',
            '広告主にとって魅力的なターゲット層にリーチできますか？',
            'コンテンツの質と広告の両立が可能ですか？'
        ]
    },
    'marketplace': {
        'name': 'マーケットプレイス型',
        'description': '取引の仲介手数料による収入モデル',
        'parameters': [
            {
                'id': 'monthly_transactions',
                'label': '月間想定取引数',
                'type': 'number',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'average_transaction',
                'label': '平均取引額',
                'type': 'number',
                'unit': '円',
                'required': True,
                'min': 0,
                'step': 1
            },
            {
                'id': 'commission_rate',
                'label': '手数料率',
                'type': 'number',
                'unit': '%',
                'required': True,
                'min': 0,
                'max': 100,
                'step': 0.1
            }
        ],
        'questions': [
            '需要と供給のマッチングが必要ですか？',
            '取引の安全性を担保できますか？',
            'プラットフォームの価値は取引量に比例しますか？'
        ]
    }
}

@revenue_wizard_bp.route('/')
@revenue_wizard_bp.route('/start')
@login_required
def wizard_start():
    """ウィザードのスタート画面を表示"""
    return render_template('revenue_wizard/start.html')

@revenue_wizard_bp.route('/questions')
@login_required
def get_questions():
    """モデル判定のための質問を返す"""
    questions = []
    for model_type, model in BUSINESS_MODELS.items():
        questions.extend(model['questions'])
    return jsonify({'questions': questions})

@revenue_wizard_bp.route('/recommend', methods=['POST'])
@login_required
def recommend_model():
    """回答に基づいてビジネスモデルを推薦"""
    answers = request.json.get('answers', {})
    
    # 各モデルのスコアを計算
    scores = {}
    for model_type, model in BUSINESS_MODELS.items():
        score = 0
        for question in model['questions']:
            if question in answers and answers[question]:
                score += 1
        scores[model_type] = score
    
    # スコアの高い順にモデルを並べ替え
    recommendations = []
    for model_type, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        model = BUSINESS_MODELS[model_type]
        recommendations.append({
            'id': model_type,
            'name': model['name'],
            'description': model['description'],
            'score': score
        })
    
    return jsonify({'recommendations': recommendations})

@revenue_wizard_bp.route('/setup/<model_type>')
@login_required
def setup_model(model_type):
    """モデルの設定画面を表示"""
    if model_type not in BUSINESS_MODELS:
        return redirect(url_for('revenue_wizard.wizard_start'))
    
    model = BUSINESS_MODELS[model_type]
    model['type'] = model_type
    return render_template('revenue_wizard/setup.html', model=model)

@revenue_wizard_bp.route('/save-model', methods=['POST'])
@login_required
def save_model():
    """モデルの設定を保存"""
    data = request.json
    
    # 現在の事業計画を取得
    business_plan = BusinessPlan.query.filter_by(
        user_id=current_user.id
    ).order_by(BusinessPlan.created_at.desc()).first()
    
    if not business_plan:
        return jsonify({'error': '事業計画が見つかりません'}), 404
    
    # 新しい収益事業モデルを作成
    revenue_model = RevenueBusinessModel(
        business_plan_id=business_plan.id,
        name=data['business_name'],
        model_type=data['model_type'],
        description=data['description'],
        parameters=data['parameters']
    )
    
    # タグを処理
    for tag_name in data.get('tags', []):
        tag = RevenueTag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = RevenueTag(name=tag_name)
            db.session.add(tag)
        revenue_model.tags.append(tag)
    
    db.session.add(revenue_model)
    db.session.commit()
    
    return jsonify({'success': True}), 201

@revenue_wizard_bp.route('/complete')
@login_required
def complete():
    """設定完了画面を表示"""
    return render_template('revenue_wizard/complete.html') 