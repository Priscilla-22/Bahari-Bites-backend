import sys
import os
import random

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.models import db, MenuItem, User
from server.app import (
    create_app,
)

from faker import Faker
from faker_food import FoodProvider

fake = Faker()
fake.add_provider(FoodProvider)
app = create_app()

categories = ['Lobster', 'Octopus', 'Prawn', 'Crab', 'Shrimp', 'Fin Fish']

# Dictionary mapping categories to their corresponding image lists
category_images = {
    'Lobster': [
        'https://images.pexels.com/photos/16743486/pexels-photo-16743486/free-photo-of-seafood-paella-with-lobster.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/20150651/pexels-photo-20150651/free-photo-of-close-up-of-a-dish-with-lobster.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/24246106/pexels-photo-24246106/free-photo-of-a-plate-with-lobster-and-vegetables.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/20943926/pexels-photo-20943926/free-photo-of-a-lobster-on-a-plate.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/16743485/pexels-photo-16743485/free-photo-of-delicious-meal-with-lobsters.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/12381101/pexels-photo-12381101.jpeg?auto=compress&cs=tinysrgb&w=600'
    ],
    'Octopus': [
        'https://images.pexels.com/photos/921361/pexels-photo-921361.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/2010702/pexels-photo-2010702.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/8352806/pexels-photo-8352806.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/1251195/pexels-photo-1251195.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/17282251/pexels-photo-17282251/free-photo-of-a-seafood-dish-with-octopus-and-a-glass-with-spritz-cocktail.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/4857728/pexels-photo-4857728.jpeg?auto=compress&cs=tinysrgb&w=600'
    ],
    'Prawn': [
        'https://images.pexels.com/photos/725997/pexels-photo-725997.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/1150447/pexels-photo-1150447.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/7363753/pexels-photo-7363753.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/6646373/pexels-photo-6646373.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/3622477/pexels-photo-3622477.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/14072789/pexels-photo-14072789.png?auto=compress&cs=tinysrgb&w=300'
    ],
    'Crab': [
        'https://images.pexels.com/photos/566345/pexels-photo-566345.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/179834/pexels-photo-179834.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/3640445/pexels-photo-3640445.jpeg?auto=compress&cs=tinysrgb&w=600'
        'https://images.pexels.com/photos/8352795/pexels-photo-8352795.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/24186319/pexels-photo-24186319/free-photo-of-crab-served-on-a-pan.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/8953624/pexels-photo-8953624.jpeg?auto=compress&cs=tinysrgb&w=300'
    ],
    'Shrimp': [
        'https://images.pexels.com/photos/3763816/pexels-photo-3763816.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/4553111/pexels-photo-4553111.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/4553111/pexels-photo-4553111.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/3009323/pexels-photo-3009323.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/12481161/pexels-photo-12481161.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/4732085/pexels-photo-4732085.jpeg?auto=compress&cs=tinysrgb&w=300'
    ],
    'Fin Fish': [
        'https://images.pexels.com/photos/262959/pexels-photo-262959.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/1683545/pexels-photo-1683545.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/16845479/pexels-photo-16845479/free-photo-of-fish-dinner-on-a-plate.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/19141512/pexels-photo-19141512/free-photo-of-fried-fish-for-dinner.jpeg?auto=compress&cs=tinysrgb&w=300https://images.pexels.com/photos/19141512/pexels-photo-19141512/free-photo-of-fried-fish-for-dinner.jpeg?auto=compress&cs=tinysrgb&w=300',
        'https://images.pexels.com/photos/19034918/pexels-photo-19034918/free-photo-of-fried-fish-and-chips-sprinkled-with-parsley.jpeg?auto=compress&cs=tinysrgb&w=600',
        'https://images.pexels.com/photos/25474365/pexels-photo-25474365/free-photo-of-fish-on-tray.jpeg?auto=compress&cs=tinysrgb&w=600'
    ]
}


with app.app_context():
    
    User.query.delete()
    print('Deleted Users')
    MenuItem.query.delete()
    print('Deleted Menu Items')
    
    admin = User(
        firstname="John",
        lastname="Kimani",
        email="johndoe@example.com",
        password="password123",
        role="admin",
        phone_number=254793453219
    )
    
    staff = User(
        firstname="Chief",
        lastname="Chef",
        email="chef@example.com",
        password="password123",
        role="staff",
        phone_number=254793453220
    )
    customer = User(
        firstname="Boina",
        lastname="Yule Mmoja",
        email="boina@example.com",
        password="password123",
        role="customer",
        phone_number=254793453221
    )
    db.session.add(admin)
    db.session.commit()
    print("Added admin user to database")
    db.session.add(customer)
    db.session.commit()
    print("Added user user to database")
    db.session.add(staff)
    db.session.commit()
    print("Added staff user to database")
    
    for x in range(100):
        category = random.choice(categories)
        image = random.choice(category_images[category])
        
        menu_item = MenuItem(
            name = fake.dish(),
            description = fake.dish_description(),
            rating = fake.random_int(min=1, max=5),
            price = fake.random_int(min=50, max=200),
            category = category,
            image_url= image
        )
        db.session.add(menu_item)
        db.session.commit()
        print("Added menu item to database")
    print('\033[92m'"Completed database population")