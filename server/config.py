#config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or "sqlite:///Bahari-Bites.sqlite"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
