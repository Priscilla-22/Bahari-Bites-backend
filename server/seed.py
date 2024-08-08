import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.models import db, MenuItem
from server.app import (
    create_app,
)
from faker import Faker

fake = Faker()
app = create_app()

img = "https://images.pexels.com/photos/725991/pexels-photo-725991.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"

with app.app_context():
    
    for x in range(10):
        menu_item = MenuItem(
            name=fake.word(),
            description=fake.text(max_nb_chars=255),
            rating=fake.random_int(min=1, max=5),
            price=fake.random_int(min=50, max=200),
            image_url=img,
        )
        db.session.add(menu_item)
        
        db.session.commit()
        print("Added menu item")