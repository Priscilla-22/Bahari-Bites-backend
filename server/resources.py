# resources.py
from flask_restful import Resource, reqparse
from models import db, User
from faker import Faker

fake = Faker()


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
        args = parser.parse_args()

        username = args["username"]
        email = args["email"]
        password = args["password"]

        if User.query.filter_by(email=email).first():
            return {"message": "Email already exists"}, 400

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return {"message": "User registered successfully"}, 201


class UserLogin(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "username", type=str, required=True, help="Username is required"
        )
        parser.add_argument(
            "password", type=str, required=True, help="Password is required"
        )
        args = parser.parse_args()

        username = args["username"]
        password = args["password"]

        fake_username = fake.user_name()
        fake_password = fake.password()

        return {
            "message": "User logged in successfully",
            "username": fake_username,
            "password": fake_password,
        }, 200
