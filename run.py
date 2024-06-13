# run.py
# run.py
from server.app import create_app
from server.mpesa import reverse_mpesa_transaction

def main():
    import os

    app = create_app()
    port = int(os.environ.get("PORT", 5000))

    with app.app_context():
        # Assuming this is where you want to call reverse_mpesa_transaction
        original_transaction_id = "SFD3DXL5ID"  # Replace with the actual transaction ID
        amount_to_reverse = 100  # Replace with the actual amount to reverse

        reverse_result = reverse_mpesa_transaction(
            original_transaction_id, amount_to_reverse
        )
        print(reverse_result)

    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
