# server/app
from flask import Flask
from flask_socketio import SocketIO
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    
    socketio.init_app(app) 

    from routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app