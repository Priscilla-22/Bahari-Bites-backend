# server/routes.py
from flask import Blueprint, send_file, current_app, jsonify
from flask_restful import Api
from .resources import (
    HomeResource,
    UserRegistration,
    UserLogin,
    CartResource,
    OrderResource,
    OrderItemResource,
    MenuItemResource,
    ReservationResource,
    InventoryResource,
)
from .mpesa import simulate_mpesa_callback
import os


api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(HomeResource, "/")
api.add_resource(UserRegistration, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(
    OrderResource, "/orders", "/orders/<int:order_id>", "/orders/<int:order_id>/status"
)
api_bp.add_url_rule(
    "/mpesa/callback",
    "simulate_mpesa_callback",
    simulate_mpesa_callback,
    methods=["POST"],
)


api.add_resource(
    OrderItemResource,
    "/orders/<int:order_id>/items",
    "/orders/<int:order_id>/items/<int:order_item_id>",
)
api.add_resource(MenuItemResource, "/menu_items", "/menu_items/<int:menu_item_id>")
api.add_resource(
    ReservationResource,
    "/reservations",
)
api.add_resource(InventoryResource, "/inventory", "/inventory/<int:inventory_id>")
api.add_resource(
    CartResource, "/cart", "/cart/<int:menu_item_id>"
) 


# download the SQLite database file.
@api_bp.route("/download_db", methods=["GET"])
def download_db():
    try:
        db_path = os.path.join(
            os.path.dirname(__file__), "..", "instance", "Bahari-Bites.sqlite"
        )
        current_app.logger.info(f"Database path: {db_path}")
        if not os.path.exists(db_path):
            current_app.logger.error(f"Database file not found at {db_path}")
            return jsonify({"error": "Database file not found"}), 404
        return send_file(
            db_path, as_attachment=True, attachment_filename="Bahari-Bites.sqlite"
        )
    except Exception as e:
        current_app.logger.error(f"Error downloading database: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500
