# server/models.py
from server.app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)


class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id_order = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    order_date = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    status = db.Column(db.String(50), nullable=False)
    user = db.relationship("User", backref=db.backref("orders", lazy=True))
    order_items = db.relationship("OrderItem", backref="order", lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    menu_item = db.relationship(
        "MenuItem", backref=db.backref("order_items", lazy=True)
    )
