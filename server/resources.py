# server/resources.py
from flask_socketio import emit
from server.app import socketio
from flask_restful import Resource, reqparse
from models import db, User, Order, OrderItem, MenuItem, Reservation
from datetime import datetime,time


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
            return {
                "message": "User logged in successfully",
                "username": user.username,
                "role": user.role,
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
        }

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument("description", type=str, required=False)
        parser.add_argument(
            "price", type=float, required=True, help="Price is required"
        )
        args = parser.parse_args()

        menu_item = MenuItem(
            name=args["name"], description=args.get("description"), price=args["price"]
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

        db.session.commit()
        return {"message": "Menu item updated successfully"}

    def delete(self, menu_item_id):
        menu_item = MenuItem.query.get(menu_item_id)
        if not menu_item:
            return {"message": "Menu item not found"}, 404

        db.session.delete(menu_item)
        db.session.commit()
        return {"message": "Menu item deleted successfully"}


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

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "user_id_order", type=int, required=True, help="User ID is required"
        )
        parser.add_argument(
            "status", type=str, required=True, help="Status is required"
        )
        parser.add_argument(
            "order_items",
            type=dict,
            action="append",
            required=True,
            help="Order items are required",
        )
        args = parser.parse_args()

        user = User.query.get(args["user_id_order"])
        if not user:
            return {"message": "User not found"}, 404

        order = Order(
            user_id_order=args["user_id_order"],
            order_date=datetime.utcnow(),
            status=args["status"],
        )
        db.session.add(order)
        db.session.commit()

        for item in args["order_items"]:
            menu_item = MenuItem.query.get(item["menu_item_id"])
            if not menu_item:
                return {
                    "message": f"Menu item with ID {item['menu_item_id']} not found"
                }, 404
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item["menu_item_id"],
                quantity=item["quantity"],
            )
            db.session.add(order_item)

        db.session.commit()

        return {"message": "Order created successfully", "order_id": order.id}, 201

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
