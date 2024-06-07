# models.py
from server.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)  
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
