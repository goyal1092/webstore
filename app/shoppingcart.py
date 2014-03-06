from flask import session, request
import random
from app import app
from models import Cart

def get_cart_id():
    if 'username' in session:
        return session['username']

    else:
        if request.cookies.get('anonymous_user'):
            cart_id = request.cookies.get('anonymous_user')
        else:
            cart_id = _genrate_cart_id()
        return cart_id


def _genrate_cart_id():
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' \
                 '1234567890!@#$%^&*()'
    cart_id_length = 50

    for y in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters)-1)]
    return cart_id

def get_cart_items():
    cart_items = Cart.query.filter_by(cart_id=get_cart_id())
    return cart_items

def cart_distinct_item_count():
    return get_cart_items().count()

def get_total_amount():
    cart = get_cart_items()
    price = 0
    for item in cart:
        price += item.products.price * item.quantity
    return price

def genrate_order_id():
    order_id = ''
    characters = '1234567890'
    order_id_length = 8
    for y in range(order_id_length):
        order_id += characters[random.randint(0, len(characters)-1)]
    return order_id

