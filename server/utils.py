from .models import (
    db,
    MpesaTransaction,
)
from datetime import datetime, time

def create_mpesa_transaction(
    payment_response, amount, phone_number, order_id=None, reservation_id=None
):
    if not order_id and not reservation_id:
        raise ValueError("Either order_id or reservation_id must be provided")

    mpesa_transaction = MpesaTransaction(
        merchant_request_id=payment_response["MerchantRequestID"],
        checkout_request_id=payment_response["CheckoutRequestID"],
        result_code=payment_response["ResponseCode"],
        result_description=payment_response["ResponseDescription"],
        amount=amount,
        mpesa_receipt_number=payment_response.get("MpesaReceiptNumber"),
        transaction_date=datetime.utcnow(),
        phone_number=phone_number,
        order_id=order_id,
        reservation_id=reservation_id,
    )
    db.session.add(mpesa_transaction)
    db.session.commit()
    return mpesa_transaction
