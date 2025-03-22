import logging
from flask import current_app, request

def setup_logging(app):
    """アプリケーションのロギング設定を行います"""
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    
    # リクエスト情報をログに記録
    @app.before_request
    def log_request_info():
        app.logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')
        if request.form:
            app.logger.debug(f'Form data: {request.form}')
    
    # レスポンス情報をログに記録
    @app.after_request
    def log_response_info(response):
        app.logger.info(f'Response: {response.status_code}')
        return response
    
    # 例外をログに記録
    @app.errorhandler(Exception)
    def log_exception(e):
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        return 'サーバーエラーが発生しました。', 500

    return app 