from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, TextAreaField, SelectField, DecimalField, IntegerField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Email, EqualTo, NumberRange, Regexp
from models import Category

def get_category():
    return Category.query.all()

class AdminLoginForm(Form):
    username = TextField('Username', validators=[Required('Username is required'), Email('Username not valid.')])
    password = PasswordField('Password', validators=[Required('Password is required')])

class CategoryForm(Form):
    name = TextField('Category', validators=[Required('Category name is required')])

class ProductForm(Form):
    category = QuerySelectField(u'Category', query_factory=get_category)
    name = TextField('Product Name', validators=[Required('Product name is required.')])
    price = DecimalField('Price', validators=[Required('Price is required')])

class UserLoginForm(Form):
    username = TextField('Username', validators=[Required('Username is required'), Email('Username not valid')])
    password = PasswordField('Password', validators=[Required('password is required')])

class SignupForm(Form):
    full_name = TextField('Name', validators=[Required('Please enter your full name.')])
    email = TextField('Email', validators=[Required('Please enter your email.'), Email('Inavild Email Address')])
    password = PasswordField('Password', validators=[Required('Password required'), EqualTo('confirm','Password does not match.')])
    confirm = PasswordField('Confirm_Password', validators=[Required('Enter confirm password')])

class QuantityForm(Form):
    quantity = IntegerField('Quantity', validators=[Required('Please eneter quantity.'), NumberRange(min=1, message='Enter valid value')], default=1)

class UserInfoForm(Form):
    name = TextField('Name', validators=[Required('please enter your name.')])
    email = TextField('Email', validators=[Required('Email is required'), Email('Username not valid')])
    phone = IntegerField('Phone Number', validators=[Required('please enter you contact number.')])
    address = TextAreaField('Address', validators=[Required('Please enter your address.')])
    city = TextField('City',validators=[Required('Please enter your city.')] )
    state = TextField('State', validators=[Required('Please enter your state.')])
    pincode = TextField('Pincode', validators=[Required('Please enter your pincode.')])

class ChangePasswordForm(Form):
    password = PasswordField('Password', validators=[Required('Password required'), EqualTo('confirm','Password does not match.')])
    confirm = PasswordField('Confirm_Password', validators=[Required('Enter confirm password')])

class AddAccountForm(Form):
    email = TextField('Email', validators=[Required('Email is required'), Email('Username not valid')])