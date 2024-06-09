# server/config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI") or "sqlite:///Bahari-Bites.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MPESA_CONSUMER_KEY = os.environ.get("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.environ.get("MPESA_CONSUMER_SECRET")
    MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE")
    MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.environ.get("MPESA_CALLBACK_URL")