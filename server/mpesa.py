# server/mpesa.py

from flask import request
from .models import db, MpesaTransaction
import requests
from requests.auth import HTTPBasicAuth
import base64
import json
from datetime import datetime
from flask import current_app
import logging
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG)


def get_mpesa_access_token():
    consumer_key = current_app.config["MPESA_CONSUMER_KEY"]
    consumer_secret = current_app.config["MPESA_CONSUMER_SECRET"]
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_header = {
        "Authorization": f"Basic {base64.b64encode(f'{consumer_key}:{consumer_secret}'.encode()).decode()}"
    }

    try:
        r = requests.get(api_url, headers=auth_header)
        mpesa_access_token = r.json()
        return mpesa_access_token["access_token"]
    except Exception as e:
        logging.error(f"Error fetching M-Pesa access token: {e}")
        raise


def lipa_na_mpesa_online(phone_number, amount, order_id):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    shortcode = current_app.config["MPESA_SHORTCODE"]
    passkey = current_app.config["MPESA_PASSKEY"]
    data_to_encode = shortcode + passkey + timestamp
    online_password = base64.b64encode(data_to_encode.encode()).decode("utf-8")

    if isinstance(amount, Decimal):
        amount = int(amount)
    elif isinstance(amount, (float, int)):
        amount = int(amount)
    else:
        raise ValueError(
            "Invalid amount type. Amount should be a Decimal, float, or int."
        )

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
    logging.info(f"Payload sent to M-Pesa API: {payload}") 

    response = requests.post(api_url, json=payload, headers=headers)
    logging.info(f"M-Pesa API response: {response.json()}")  

    return response.json()


def simulate_mpesa_api_call(phone_number, amount, order_id):
    """
    Simulates an M-Pesa API call for testing purposes.
    """
    response = {
        "MerchantRequestID": "12345",
        "CheckoutRequestID": "67890",
        "ResponseCode": "0",
        "ResponseDescription": "Success. Request accepted for processing",
        "CustomerMessage": "Success. Request accepted for processing",
    }

    callback_data={
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": response["MerchantRequestID"],
                    "CheckoutRequestID": response["CheckoutRequestID"],
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": amount},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123XYZ"},
                            {
                                "Name": "TransactionDate",
                                "Value": datetime.now().strftime("%Y%m%d%H%M%S"),
                            },
                            {"Name": "PhoneNumber", "Value": phone_number},
                        ]
                    },
                }
            }
    }
    simulate_mpesa_callback(callback_data,order_id)
    logging.info(f"Simulated M-Pesa API response: {response}")
    return response


def reverse_mpesa_transaction(original_transaction_id, amount):
    access_token = get_mpesa_access_token()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/reversal/v1/request"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    shortcode = current_app.config["MPESA_SHORTCODE"]
    security_credential = current_app.config["MPESA_SECURITY_CREDENTIAL"]

    payload = {
        "Initiator": "testapi",
        "SecurityCredential": security_credential,
        "CommandID": "TransactionReversal",
        "TransactionID": original_transaction_id,
        "Amount": amount,
        "ReceiverParty": shortcode,
        "RecieverIdentifierType": 11,
        "Remarks": "Incorrect transaction amount reversal",
        "QueueTimeOutURL": current_app.config["MPESA_CALLBACK_URL"],
        "ResultURL": current_app.config["MPESA_CALLBACK_URL"],
    }

    logging.info(f"Payload sent for M-Pesa reversal: {payload}")

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        logging.info(f"M-Pesa reversal API response: {response.json()}")
        return response.json()
    except Exception as e:
        logging.error(f"Error reversing transaction: {e}")
        raise


def initiate_mpesa_transaction(phone_number, amount, order_id, simulate=False):
    if simulate:
        return simulate_mpesa_api_call(phone_number, amount, order_id)
    else:
        amount = Decimal(amount)
        logging.info(f"Initiating M-Pesa transaction with amount: {amount}")
        return lipa_na_mpesa_online(phone_number, amount, order_id)


def simulate_mpesa_callback(data, order_id):
    """
    Simulate M-Pesa callback to mimic real-world scenario for testing.
    """
    if data is None:
        logging.error("No callback data provided")
        return {"ResultCode": 1, "ResultDesc": "No callback data provided"}, 400
    
    logging.info(f"M-Pesa Callback data: {data}")

    result_code = data["Body"]["stkCallback"]["ResultCode"]
    result_desc = data["Body"]["stkCallback"]["ResultDesc"]
    merchant_request_id = data["Body"]["stkCallback"]["MerchantRequestID"]
    checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
    callback_metadata = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

    amount = next(
        item["Value"] for item in callback_metadata if item["Name"] == "Amount"
    )
    mpesa_receipt_number = next(
        item["Value"]
        for item in callback_metadata
        if item["Name"] == "MpesaReceiptNumber"
    )
    transaction_date = next(
        item["Value"] for item in callback_metadata if item["Name"] == "TransactionDate"
    )
    phone_number = next(
        item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"
    )

    order_id = request.args.get("order_id")

    if not order_id:
        logging.error("Order ID not found in callback request")
        return {"ResultCode": 1, "ResultDesc": "Order ID not found"}, 400

    transaction = MpesaTransaction(
        merchant_request_id=merchant_request_id,
        checkout_request_id=checkout_request_id,
        result_code=result_code,
        result_description=result_desc,
        amount=Decimal(amount),
        mpesa_receipt_number=mpesa_receipt_number,
        transaction_date=datetime.strptime(str(transaction_date), "%Y%m%d%H%M%S"),
        phone_number=phone_number,
        order_id=order_id,
    )
    db.session.add(transaction)
    db.session.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}
