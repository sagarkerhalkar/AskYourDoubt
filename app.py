from __future__ import annotations

from pathlib import Path
import os

from flask import Flask, render_template

from config import Config
from db import init_app as init_db


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    for key in ('UPLOAD_DOUBTS', 'UPLOAD_RESOURCES', 'QR_FOLDER', 'EXPORT_FOLDER'):
        Path(app.config[key]).mkdir(parents=True, exist_ok=True)

    init_db(app)

    from routes.public import bp as public_bp
    from routes.student import bp as student_bp
    from routes.teacher import bp as teacher_bp
    from routes.admin import bp as admin_bp
    from routes.api import bp as api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_):
        return render_template('public/error.html', code=404, title='Page not found', message='The page you requested does not exist.'), 404

    @app.errorhandler(413)
    def too_large(_):
        return render_template('public/error.html', code=413, title='File too large', message='The maximum upload size is 10 MB.'), 413

    @app.context_processor
    def inject_brand():
        from db import get_db
        row = get_db().execute("SELECT setting_value FROM app_settings WHERE setting_key='logo_path'").fetchone()
        return {'brand_logo': row['setting_value'] if row else '/static/img/logo.svg'}

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('AYD_PORT', '9000')), debug=os.getenv('AYD_DEBUG') == '1')
