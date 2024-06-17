# server/app
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager
from flask_mail import Mail


load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

db = SQLAlchemy()
socketio = SocketIO()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    db.init_app(app)
    migrate = Migrate(app, db)

    # socketio.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    jwt = JWTManager(app)

    from .routes import api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    mail.init_app(app)
    return app
