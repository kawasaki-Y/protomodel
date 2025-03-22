from flask import Blueprint, send_from_directory, current_app
import os

bp = Blueprint('static', __name__)

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    ) 