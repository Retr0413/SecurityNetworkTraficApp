from flask import Flask
from app.routes.api import api_bp
from app.routes.frontend import frontend_bp
from app.config import Config
from app.utils import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(frontend_bp, url_prefix='/')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)  