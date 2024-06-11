# server/models.py
from server.app import db
from sqlalchemy.orm import relationship


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    cart = db.relationship('Cart', backref='user', uselist=False)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255))
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.id"))
    inventory = db.relationship(
        "Inventory", backref=db.backref("menu_item", uselist=False)
    )


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = relationship("CartItem", backref="cart")


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("cart.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    menu_item = db.relationship("MenuItem")


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_order = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_date = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    status = db.Column(db.String(50), nullable=False)
    user = db.relationship("User", backref=db.backref("orders", lazy=True))
    order_items = db.relationship("OrderItem", backref="order", lazy=True)
    phone_number = db.Column(
        db.String(15), nullable=False
    )  

    def __repr__(self):
        return f"<Order {self.id}>"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    menu_item = db.relationship(
        "MenuItem", backref=db.backref("order_items", lazy=True)
    )


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_reservation = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    reservation_date = db.Column(db.DateTime, nullable=False)
    table_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Reservation {self.id}>"


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class MpesaTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_request_id = db.Column(db.String(100), nullable=False)
    checkout_request_id = db.Column(db.String(100), nullable=False)
    result_code = db.Column(db.Integer, nullable=False)
    result_description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    mpesa_receipt_number = db.Column(db.String(50))
    transaction_date = db.Column(db.DateTime)
    phone_number = db.Column(db.String(15), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    order = db.relationship(
        "Order", backref=db.backref("mpesa_transactions", lazy=True)
    )

    def __repr__(self):
        return f"<MpesaTransaction {self.id}>"
