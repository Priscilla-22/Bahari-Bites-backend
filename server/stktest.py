import sys
import os
import random

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from server.models import db, MenuItem, User
from server.app import (
    create_app,
)
from server.mpesa import initiate_mpesa_transaction

# Initialize the Flask app context
app = create_app()

with app.app_context():
    # Replace these with valid test values
    phone_number = "254722862787"
    amount = 1
    order_id = "test_order_123"
    simulate = False  # Set to False to make a real API call

    # Call the functions
    response = initiate_mpesa_transaction(phone_number, amount, order_id, simulate)

    print("Response:", response)
