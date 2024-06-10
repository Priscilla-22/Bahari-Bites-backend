# server/mpesa.py
from flask import request
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from datetime import datetime
from flask import current_app
import logging

logging.basicConfig(level=logging.DEBUG)


def get_mpesa_access_token():
    consumer_key = current_app.config["MPESA_CONSUMER_KEY"]
    consumer_secret = current_app.config["MPESA_CONSUMER_SECRET"]
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    logging.debug(f"MPesa API Response: {r.text}")  

    try:
        mpesa_access_token = json.loads(r.text)
        return mpesa_access_token["access_token"]
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed: {e}")
        logging.error(f"Response content: {r.text}")
        raise ValueError("Failed to decode JSON from MPesa API response")


def lipa_na_mpesa_online(phone_number, amount, order_id):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = current_app.config["MPESA_SHORTCODE"]
    passkey = current_app.config["MPESA_PASSKEY"]
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

    payload = {
        "BusinessShortCode": shortcode,
        "Password": online_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": current_app.config["MPESA_CALLBACK_URL"],
        "AccountReference": order_id,
        "TransactionDesc": "Payment for order {}".format(order_id),
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def mpesa_callback():
    data = json.loads(request.data)
    print("M-Pesa Callback data: ", data)
    return {"ResultCode": 0, "ResultDesc": "Accepted"}
