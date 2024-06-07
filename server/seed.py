# server/seed.py
from faker import Faker
from server.models import db, User  
from server.app import (
    create_app,
)

fake = Faker()


def seed_users(num_users=10):
    app = create_app()
    with app.app_context():
        for _ in range(num_users):
            username = fake.user_name()
            password = fake.password()
            role = "customer"
            user = User(username=username, password=password, role=role)
            db.session.add(user)
        db.session.commit()


if __name__ == "__main__":
    seed_users()
