# models.py
from server.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)  # Add this line
    password = db.Column(db.String(100), nullable=False)
