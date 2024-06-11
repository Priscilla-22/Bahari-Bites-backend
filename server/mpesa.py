# server/mpesa.py
from flask import request
from .models import MpesaTransaction, db
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from datetime import datetime
from flask import current_app
import logging
import decimal


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
        "Amount": str(amount),
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

    # Extract required fields from the callback data
    callback = data.get("Body", {}).get("stkCallback", {})
    merchant_request_id = callback.get("MerchantRequestID")
    checkout_request_id = callback.get("CheckoutRequestID")
    result_code = callback.get("ResultCode")
    result_desc = callback.get("ResultDesc")

    # Initialize values
    amount = None
    mpesa_receipt_number = None
    transaction_date = None
    phone_number = None

    # Retrieve callback metadata if available
    callback_metadata = callback.get("CallbackMetadata", {}).get("Item", [])
    for item in callback_metadata:
        name = item.get("Name")
        value = item.get("Value")
        if name == "Amount":
            amount = decimal.Decimal(value)
        elif name == "MpesaReceiptNumber":
            mpesa_receipt_number = value
        elif name == "TransactionDate":
            transaction_date = datetime.strptime(str(value), "%Y%m%d%H%M%S")
        elif name == "PhoneNumber":
            phone_number = value

    # Assuming you pass order_id in AccountReference, extract it if needed
    order_id = None
    if "AccountReference" in request.json:
        order_id = request.json["AccountReference"]

    # Create a new MpesaTransaction record
    mpesa_transaction = MpesaTransaction(
        merchant_request_id=merchant_request_id,
        checkout_request_id=checkout_request_id,
        result_code=result_code,
        result_description=result_desc,
        amount=amount,
        mpesa_receipt_number=mpesa_receipt_number,
        transaction_date=transaction_date,
        phone_number=phone_number,
        order_id=order_id,
    )

    # Save to the database
    db.session.add(mpesa_transaction)
    db.session.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
