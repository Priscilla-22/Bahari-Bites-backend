# server/routes.py
from flask import Blueprint, send_file
from flask_restful import Api
from flask import Response
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
    LiveChatResource,
    BranchResource,
    Menu
)
from .mpesa import simulate_mpesa_callback
import os


api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(HomeResource, "/")
api.add_resource(UserRegistration, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(Menu, "/menu")

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
api.add_resource(LiveChatResource, "/live_chat")
api.add_resource(BranchResource, "/branches" ,"/branches/<int:branch_id>")


# download the SQLite database file.
@api_bp.route("/download_db", methods=["GET"])
def download_db():
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "instance", "Bahari-Bites.sqlite"
    )
    response = send_file(db_path, as_attachment=True, download_name="Bahari-Bites.sqlite")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
