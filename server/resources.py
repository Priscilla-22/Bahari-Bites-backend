# server/resources.py
from flask import jsonify,request
from twilio.base.exceptions import TwilioRestException
from flask_jwt_extended import jwt_required, get_jwt_identity,create_access_token
from flask_socketio import emit
from server.app import socketio
from flask_restful import Resource, reqparse
from .models import (
    db,
    User,
    Order,
    OrderItem,
    MenuItem,
    Reservation,
    Inventory,
    Cart,
    CartItem,
    MpesaTransaction,
)
from datetime import datetime,time
from .mpesa import (
    lipa_na_mpesa_online,
    simulate_mpesa_callback,
    initiate_mpesa_transaction,
)
from decimal import Decimal
from twilio.rest import Client
import os
import logging
from flask import current_app
import re


class HomeResource(Resource):
    def get(self):
        return jsonify({"message": "Welcome to Bahari Bites"})


class UserRegistration(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, required=True, help="Username is required"
        )
        parser.add_argument("email", type=str, required=True, help="Email is required")
        parser.add_argument(
            "password", type=str, required=True, help="Password is required"
        )
        parser.add_argument(
            "role",
            type=str,
            required=True,
            help="Role is required (customer, staff, or admin)",
        )
        args = parser.parse_args()

        username = args["username"]
        email = args["email"]
        password = args["password"]
        role = args["role"]

        if User.query.filter_by(username=username).first():
            return {"message": "Username already exists"}, 400

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400

        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "credential", type=str, required=True, help="Username or email is required"
        )
        parser.add_argument(
            "password", type=str, required=True, help="Password is required"
        )
        args = parser.parse_args()

        credential = args["credential"]
        password = args["password"]

        user = User.query.filter(
            (User.username == credential) | (User.email == credential)
        ).first()
        
        if user and user.password == password:

            access_token = create_access_token(identity=user.id)
            return {
                "message": "User logged in successfully",
                "username": user.username,
                "role": user.role,
                "access_token": access_token  
            }, 200
        else:
            return {"message": "Invalid username, email, or password"}, 401


class MenuItemResource(Resource):
    def get(self, menu_item_id):
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {"message": "Menu item not found"}, 404
        return {
            "id": menu_item.id,
            "name": menu_item.name,
            "description": menu_item.description,
            "price": str(menu_item.price),
            "image_url": menu_item.image_url,
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument("description", type=str, required=False)
        parser.add_argument(
            "price", type=float, required=True, help="Price is required"
        )
        parser.add_argument(
            "image_url", type=str, required=False, help="Image URL is optional"
        )
        args = parser.parse_args()

        menu_item = MenuItem(
            name=args["name"],
            description=args.get("description"),
            price=args["price"],
            image_url=args.get("image_url"),
        )
        db.session.add(menu_item)
        db.session.commit()

        return {
            "message": "Menu item created successfully",
            "menu_item_id": menu_item.id,
        }, 201

    def put(self, menu_item_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=False)
        parser.add_argument("description", type=str, required=False)
        parser.add_argument("price", type=float, required=False)
        parser.add_argument("image_url", type=str, required=False)  

        args = parser.parse_args()

        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {"message": "Menu item not found"}, 404

        if args["name"]:
            menu_item.name = args["name"]
        if args["description"]:
            menu_item.description = args["description"]
        if args["price"]:
            menu_item.price = args["price"]
        if args["image_url"]:
            menu_item.image_url = args["image_url"] 
        db.session.commit()
        return {"message": "Menu item updated successfully"}

    def delete(self, menu_item_id):
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {"message": "Menu item not found"}, 404

        db.session.delete(menu_item)
        db.session.commit()
        return {"message": "Menu item deleted successfully"}


class CartResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not user_cart:
            return {"message": "Cart is empty"}

        cart_items = [
            {
                "id": cart_item.menu_item.id,
                "name": cart_item.menu_item.name,
                "quantity": cart_item.quantity,
            }
            for cart_item in user_cart.items
        ]
        return jsonify(cart_items)

    @jwt_required()
    def post(self, menu_item_id):
        current_user_id = get_jwt_identity()
        user_cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not user_cart:
            user_cart = Cart(user_id=current_user_id)
            db.session.add(user_cart)
            db.session.commit()

        quantity = request.json.get("quantity", 1)
        cart_item = CartItem.query.filter_by(
            cart_id=user_cart.id, menu_item_id=menu_item_id
        ).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=user_cart.id, menu_item_id=menu_item_id, quantity=quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        return {"message": "Item added to cart successfully"}

    @jwt_required()
    def delete(self, menu_item_id):
        current_user_id = get_jwt_identity()
        user_cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not user_cart:
            return {"message": "Cart is empty"}

        cart_item = CartItem.query.filter_by(
            cart_id=user_cart.id, menu_item_id=menu_item_id
        ).first()
        if not cart_item:
            return {"message": "Item not found in cart"}

        db.session.delete(cart_item)
        db.session.commit()
        return {"message": "Item removed from cart successfully"}


class OrderResource(Resource):
    def get(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        order_items = [
            {
                "id": item.id,
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "menu_item_name": item.menu_item.name,
                "menu_item_price": str(item.menu_item.price),
            }
            for item in order.order_items
        ]

        return {
            "id": order.id,
            "user_id_order": order.user_id_order,
            "order_date": order.order_date.isoformat(),
            "status": order.status,
            "order_items": order_items,
        }

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        user_cart = Cart.query.filter_by(user_id=current_user_id).first()
        if not user_cart:
            return {"message": "Cart is empty"}, 400

        parser = reqparse.RequestParser()
        parser.add_argument(
            "phone_number",
            type=str,
            required=True,
            help="Phone number is required for payment",
        )
        parser.add_argument(
            "simulate",
            type=bool,
            required=False,
            default=False,
            help="Set to true to simulate M-Pesa transaction",
        )
        args = parser.parse_args()

        total_amount = Decimal(0.00)
        order_items = []
        for cart_item in user_cart.items:
            order_items.append(
                OrderItem(
                    menu_item_id=cart_item.menu_item_id, quantity=cart_item.quantity
                )
            )

            total_amount += cart_item.menu_item.price * cart_item.quantity
        current_app.logger.info(f"Total amount calculated: {total_amount}")

        if total_amount < Decimal(0) or total_amount > Decimal(70000):
            return {"message": "Invalid total amount for M-Pesa transaction"}, 400

        total_amount_formatted = str(total_amount)
        current_app.logger.info(
            f"Formatted total amount for M-Pesa transaction: {total_amount_formatted}"
        )

        order = Order(
            user_id_order=current_user_id,
            order_date=datetime.utcnow(),
            status="Pending",
            phone_number=args["phone_number"],
        )
        order.order_items = order_items
        db.session.add(order)
        db.session.commit()

        payment_response = initiate_mpesa_transaction(
            args["phone_number"],
            total_amount,
            order.id,
            simulate=args["simulate"],
        )

        if args["simulate"]:
            simulate_mpesa_callback(payment_response)

        if payment_response.get("ResponseCode") == "0":
            mpesa_transaction = MpesaTransaction(
                merchant_request_id=payment_response["MerchantRequestID"],
                checkout_request_id=payment_response["CheckoutRequestID"],
                result_code=payment_response["ResponseCode"],
                result_description=payment_response["ResponseDescription"],
                amount=total_amount,
                mpesa_receipt_number=payment_response.get("MpesaReceiptNumber"),
                transaction_date=datetime.utcnow(),
                phone_number=args["phone_number"],
               order_id=order.id,
            )
            db.session.add(mpesa_transaction)
            db.session.commit()

      
            CartItem.query.filter_by(cart_id=user_cart.id).delete()
            db.session.commit()

            forwarding_number = self.get_forwarding_number(order.id)
            self.send_order_confirmation_sms(
                order.id, args["phone_number"], forwarding_number
            )
            return {
                "message": "Order created and payment initiated successfully",
                "order_id": order.id,
            }, 201
        else:
            return {
                "message": "Order created but payment failed",
                "order_id": order.id,
                "payment_error": payment_response,
            }, 400

    def get_forwarding_number(self, order_id):
        mpesa_transaction = MpesaTransaction.query.filter_by(order_id=order_id).first()
        if mpesa_transaction:
            return mpesa_transaction.phone_number
        return None

    def send_order_confirmation_sms(self, order_id, phone_number, forwarding_number):
        order = Order.query.get(order_id)
        if not order:
            return

        order_summary = "\n".join(
            [f"{item.menu_item.name} (x{item.quantity})" for item in order.order_items]
        )

        message = f"Order Confirmation\nOrder ID: {order.id}\nEstimated Delivery: 30 mins\nOrder Summary:\n{order_summary}"
        current_app.logger.info(f"Sending SMS to: {phone_number}")

        self.send_sms(phone_number, message, forwarding_number)

    def send_sms(self, phone_number, message, forwarding_number):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        client = Client(account_sid, auth_token)

        phone_number = self.normalize_phone_number(phone_number)
        if not phone_number or not self.validate_phone_number(phone_number):
            current_app.logger.error(f"Invalid phone number format: {phone_number}")
            return

        try:
            client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )

            if forwarding_number:
                forwarding_number = self.normalize_phone_number(forwarding_number)
                if self.validate_phone_number(forwarding_number):
                    client.messages.create(
                        body=f"Forwarded Message: {message}",
                        from_=from_number,
                        to=forwarding_number
                    )

        except TwilioRestException as e:
            current_app.logger.error(f"Twilio Error: {e}")

    def normalize_phone_number(self, phone_number):
        if not phone_number.startswith('+'):
            phone_number = f'+{phone_number}'
        return phone_number

    def validate_phone_number(self, phone_number):
        return re.match(r'^\+?[1-9]\d{1,14}$', phone_number) is not None
            
            
    def put(self, order_id):
        parser = reqparse.RequestParser()
        parser.add_argument("status", type=str, required=False)
        args = parser.parse_args()

        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        if args["status"]:
            order.status = args["status"]

        db.session.commit()
        return {"message": "Order updated successfully"}

    def delete(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        db.session.delete(order)
        db.session.commit()
        return {"message": "Order deleted successfully"}

    def get_status(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404
        return {"status": order.status}

    def update_status(self, order_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "status", type=str, required=True, help="Status is required"
        )
        args = parser.parse_args()

        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        old_status = order.status
        order.status = args["status"]
        db.session.commit()

        socketio.emit('order_status_update', {'order_id': order_id, 'old_status': old_status, 'new_status': order.status}, namespace='/order')

        return {"message": "Order status updated successfully"}


class OrderItemResource(Resource):
    def post(self, order_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "menu_item_id", type=int, required=True, help="Menu item ID is required"
        )
        parser.add_argument(
            "quantity", type=int, required=True, help="Quantity is required"
        )
        args = parser.parse_args()

        order = Order.query.get(order_id)
        if not order:
            return {"message": "Order not found"}, 404

        menu_item = MenuItem.query.get(args["menu_item_id"])
        if not menu_item:
            return {
                "message": f"Menu item with ID {args['menu_item_id']} not found"
            }, 404

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=args["menu_item_id"],
            quantity=args["quantity"],
        )
        db.session.add(order_item)
        db.session.commit()

        return {
            "message": "Order item added successfully",
            "order_item_id": order_item.id,
        }, 201

    def delete(self, order_id, order_item_id):
        order_item = OrderItem.query.filter_by(
            order_id=order_id, id=order_item_id
        ).first()
        if not order_item:
            return {"message": "Order item not found"}, 404

        db.session.delete(order_item)
        db.session.commit()
        return {"message": "Order item deleted successfully"}


class ReservationResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "user_id_reservation",
            type=int,
            required=True,
            help="User ID is required for reservation",
        )
        parser.add_argument(
            "reservation_date",
            type=str,
            required=True,
            help="Reservation date is required (format: YYYY-MM-DD HH:MM:SS)",
        )
        parser.add_argument(
            "table_number",
            type=int,
            required=True,
            help="Table number is required for reservation",
        )
        args = parser.parse_args()

        user = User.query.get(args["user_id_reservation"])
        if not user:
            return {"message": "User not found"}, 404

        reservation_date = datetime.strptime(
            args["reservation_date"], "%Y-%m-%d %H:%M:%S"
        )

       
        reservation_cost = calculate_reservation_cost(reservation_date.time())

        reservation = Reservation(
            user_id_reservation=args["user_id_reservation"],
            reservation_date=reservation_date,
            table_number=args["table_number"],
        )
        db.session.add(reservation)
        db.session.commit()

        return {
            "message": "Reservation created successfully",
            "reservation_id": reservation.id,
            "reservation_cost": reservation_cost,
        }, 201


def calculate_reservation_cost(reservation_time):
    if reservation_time < time(12, 0):  
        return 30 
    elif reservation_time < time(18, 0):  
        return 50  
    else:
        return 70 


class InventoryResource(Resource):
    def get(self, inventory_id):
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return {"message": "Inventory item not found"}, 404
        return {
            "id": inventory.id,
            "item_name": inventory.item_name,
            "quantity": inventory.quantity,
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "item_name", type=str, required=True, help="Item name is required"
        )
        parser.add_argument(
            "quantity", type=int, required=True, help="Quantity is required"
        )
        args = parser.parse_args()

        inventory = Inventory(item_name=args["item_name"], quantity=args["quantity"])
        db.session.add(inventory)
        db.session.commit()

        return {
            "message": "Inventory item created successfully",
            "inventory_id": inventory.id,
        }, 201

    def put(self, inventory_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "quantity", type=int, required=True, help="Quantity is required"
        )
        args = parser.parse_args()

        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return {"message": "Inventory item not found"}, 404

        inventory.quantity = args["quantity"]
        db.session.commit()

        socketio.emit(
            "stock_update",
            {"inventory_id": inventory_id, "new_quantity": args["quantity"]},
            namespace="/inventory",
        )

        return {"message": "Inventory item updated successfully"}

    def delete(self, inventory_id):
        inventory = Inventory.query.get(inventory_id)
        if not inventory:
            return {"message": "Inventory item not found"}, 404

        db.session.delete(inventory)
        db.session.commit()
        return {"message": "Inventory item deleted successfully"}


class LiveChatResource(Resource):
    @jwt_required()
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "message", type=str, required=True, help="Message is required"
        )
        parser.add_argument("room", type=str, required=True, help="Room is required")
        args = parser.parse_args()

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        message = args["message"]
        room = args["room"]

        socketio.emit("message", {"msg": message, "username": user.username}, room=room)
        return {"message": "Message sent"}
