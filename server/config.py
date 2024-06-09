# server/config.py
import os


class Config:
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI") or "sqlite:///Bahari-Bites.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MPESA_CONSUMER_KEY = os.environ.get(
        "UGUC1ZsTG7mwIC44IbCw95uBU6R8C4kSdb94qjGXTcWNSqim"
    )
    MPESA_CONSUMER_SECRET = os.environ.get(
        "oa7SwdPfrky8AFVSxXgzj2cjqbMGSmqB1hNRtAes8buVF36GT1b69UGYnAhgMaU3"
    )
    MPESA_SHORTCODE = os.environ.get("MPESA_SHORTCODE")
    MPESA_PASSKEY = os.environ.get("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.environ.get("https://bahari-bites-backend.onrender.com")
