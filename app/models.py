from app import db
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, username, password):
        self.username = username.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return self.username

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return self.name

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True)
    price = db.Column(db.Float, index=True)
    description = db.Column(db.String(400), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    cart = db.relationship('Cart', backref='products', lazy='dynamic')

    def __repr__(self):
        return self.name

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))
    date = db.Column(db.DATETIME)
    name = db.Column(db.String(100))
    user_info = db.relationship('UserInfo', uselist=False, backref="user_information")

    def __init__(self, email, password, name):
        self.email = email.lower()
        self.set_password(password)
        self.name = name
        self.date = datetime.date.today()

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def __repr__(self):
        return self.name

class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.Integer, unique=True)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    pincode = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer)
    date = db.Column(db.DATETIME)
    quantity = db.Column(db.Integer)
    product = db.Column(db.Integer, db.ForeignKey('product.id'))

    def augment_quantity(self, quantity):
        self.quantity += int(quantity)
        return self.quantity

class OrderId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, unique=True)
    buyer_name = db.Column(db.String(60))
    buyer_address = db.Column(db.String(200))
    total_products = db.Column(db.Integer)
    date = db.Column(db.DATE)
    email = db.Column(db.String(120))
    phone = db.Column(db.Integer)


class Ordered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)
    order_id = db.Column(db.Integer)