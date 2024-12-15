from flask import Flask
from app.utils.db import db
from app.utils.config import Config
from app.routes.api import api_bp
from app.routes.frontend import front_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(front_bp, url_prefix='/')
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
