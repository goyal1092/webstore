from app import app, db, shoppingcart
from flask import render_template, redirect, url_for, flash, make_response, request, session
from flask.ext.login import login_required, login_user, logout_user
from models import Admin
from forms import AdminLoginForm, CategoryForm, ProductForm, SignupForm, UserLoginForm, QuantityForm, UserInfoForm, ChangePasswordForm
from models import Category, Product, User, Cart, Ordered, OrderId
import datetime
from email import signup, order_email
from math import isnan


@app.route('/base/')
def base():
    return render_template('base.html')

# User Login and Home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
    count = shoppingcart.cart_distinct_item_count()
    form = UserLoginForm()
    signup = SignupForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.username.data).first()
        if form.validate_on_submit():
            if user:
                if user.check_password(form.password.data):
                    session['username'] = user.email
                    flash('login succesful','text-success')
                    resp = make_response(render_template('home.html', user=user, count=count))
                    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
                    return resp
            flash('Login not valid', 'text-danger')

    return render_template('home.html', form=form, count=count, signup_form=signup)

# User Logout
@app.route('/user/logout/')
def user_logout():

    if 'username' in session:
        session.pop('username', None)
        session.clear()
        resp = make_response(redirect(url_for('index')))
        resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
        return resp
    else:
        return redirect(url_for('index'))
# Signup Form
@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    form = SignupForm()
    count = shoppingcart.cart_distinct_item_count()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, name=form.full_name.data.title())
        db.session.add(user)
        try:
            db.session.commit()

            signup([form.email.data])
            flash('Thank you for signing up. ')
        except:
            db.session.rollback()
            raise

        return redirect(url_for('index'))
    return render_template('signup.html', form=form, count=count)


# Catalog
@app.route('/catalog/', methods=['GET', 'POST'])
def catalog():
    count = shoppingcart.cart_distinct_item_count()
    form = QuantityForm()
    if request.method == 'POST':
        key = request.form['product_slug']
        product_id = Product.query.get(key)
        quantity = request.form['quantity']
        if quantity == '' or int(quantity)< 1:
            flash('please enter valid quantity','text-danger')
            return redirect(url_for('catalog'))
        get_cart_id = shoppingcart.get_cart_id()
        date = datetime.date.today()
        cart_products = shoppingcart.get_cart_items()
        product_in_cart = False
        for item in cart_products:
            if item.product == int(key):
                item.quantity = item.quantity + int(quantity)
                db.session.commit()
                product_in_cart = True
        if not product_in_cart:
            cart = Cart(cart_id=get_cart_id, date=date, quantity=quantity, products=product_id)
            db.session.add(cart)
            db.session.commit()
        if 'username' in session:
            return redirect(url_for('cart'))
        else:
            resp = make_response(redirect('/cart'))
            resp.set_cookie('anonymous_user', get_cart_id)
            return resp
    category = Category.query.all()
    product = Product.query.all()
    return render_template('catalog.html', categories=category, products=product, form=form, count=count)


@app.route('/cart/', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        val = request.form['submit']
        id = request.form['cart_info']
        cart = Cart.query.get(id)
        if val == 'Remove':
            db.session.delete(cart)
            db.session.commit()
        if val == 'Save':
            quantity = request.form['update_quantity']
            if int(quantity) < 1:
                db.session.delete(cart)
                flash('quantity should be greater than or equal to 1.')
            else:
                cart.quantity = quantity
            db.session.commit()
    total_amount = shoppingcart.get_total_amount()
    cart = shoppingcart.get_cart_items()
    product_no = shoppingcart.cart_distinct_item_count()
    return render_template('cart.html', cart=cart, count=product_no, total=total_amount)


# Admin Login
@app.route('/admin/login/', methods=['GET', 'POST'])

def admin_login():
    form = AdminLoginForm()
    admin = Admin.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            resp = make_response(render_template('admin-panel/admin-base.html'))
            resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
            return resp
        else:
            flash('Check your username and password.','text-danger')
    return render_template('admin-login.html', form=form)

# Admin Logout
@app.route('/logout/')
@login_required
def admin_logout():
    logout_user()
    resp = make_response(redirect(url_for('index')))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp



# Home Page of Admin-Panel
@app.route('/admin/home/')
@login_required
def admin_base():
    return render_template('admin-panel/admin-base.html')

# Add Category to Database
@app.route('/admin/category/add/', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data.title())
        db.session.add(category)
        try:
            db.session.commit()
            flash("category named "+ category.name + " is added to database.")
        except:
            db.session.rollback()
            raise

        return redirect(url_for('add_category'))
    categories = Category.query.all()
    return render_template('admin-panel/category.html', form=form, categories=categories)

# Delete Category from Database
@app.route('/admin/category/delete/<int:pk>/')
@login_required
def delete_category(pk):
    category = Category.query.get(pk)
    product = Product.query.filter_by(category_id=pk)
    if product:
        for item in product:
            db.session.delete(item)
    db.session.delete(category)
    db.session.commit()
    flash("Category named "+ category.name +" is deleted.")
    return redirect(url_for('add_category'))

# Edit Category in Database
@app.route('/admin/category/edit/<int:pk>/', methods=['GET','POST'])
@login_required
def edit_category(pk):
    category= Category.query.get(pk)
    categories = Category.query.all()
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.add(category)
        db.session.commit()
        flash("Category edited")
        return redirect(url_for('add_category'))
    return render_template('admin-panel/edit-category.html', title='Edit', form=form, categories=categories,
                           category=category)

# Add Product in Database
@app.route('/admin/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data.title(), price=form.price.data, category=form.category.data)
        db.session.add(product)
        try:
            db.session.commit()
            flash(product.name + " added")
        except:
            db.session.rollback()
            raise
        return redirect(url_for('add_product'))
    product = Product.query.all()
    return render_template('admin-panel/product.html', form=form, product=product)

# Delete Product from Database
@app.route('/admin/product/delete/<int:pk>')
@login_required
def delete_product(pk):
    product = Product.query.get(pk)
    db.session.delete(product)
    try:
        db.session.commit()
        flash(product.name + " deleted")
    except:
        db.session.rollback()
        raise
    return redirect(url_for('add_product'))

# Edit Produt in Database
@app.route('/admin/product/edit/<int:pk>',  methods=['GET','POST'])
@login_required
def edit_product(pk):
    products = Product.query.all()
    product = Product.query.get(pk)
    categories = Category.query.all()
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.category = form.category.data
        product.price = form.price.data
        db.session.add(product)
        db.session.commit()
        flash("Product saved.")
        return redirect(url_for("add_product"))
    return render_template("admin-panel/edit-product.html", product=product, products=products,
                           form=form, categories=categories)

@app.route('/admin/order_list')
@login_required
def orders():
    order = OrderId.query.all()
    return render_template('admin-panel/orders.html', orders=order)


@app.route('/admin/order/<int:pk>', methods=['GET', 'POST'])
@login_required
def specific_order(pk):
    order = OrderId.query.get(pk)
    ordered_products = Ordered.query.filter_by(order_id=order.order_id)
    return render_template('admin-panel/specific_order.html', order=order,products=ordered_products)


'''User Account'''

#  Add info
@app.route('/user/account')
def user_info():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(email=username)
        form = UserInfoForm()
        return render_template('user-panel/user_info.html', user=user, form=form)
    else:
        flash('Please Login')
        return redirect(url_for('index'))
@app.route('/user/account/edit')
def edit_info():
    if 'username' in session:
        form = UserInfoForm()
        return render_template('user-panel/edit_info.html', form=form)
    else:
        flash('Please Login')
        return redirect(url_for('index'))

@app.route('/user/account/change_password')
def edit_password():
    if 'username' in session:
        form = ChangePasswordForm()
        return render_template('user-panel/edit_password.html', form=form)
    else:
        flash('Please Login')
        return redirect(url_for('index'))

@app.route('/checkout/details', methods=['GET', 'POST'])
def checkout_details():
    form = UserInfoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cd = {
                'name': request.form['name'],
                'phone': request.form['phone_no'],
                'address': request.form['address']+', '+ request.form['city']+'-'+request.form['state']+' ('+request.form['pincode']+')',
                'email':request.form['email']
            }
            session['details'] = cd
            cart = shoppingcart.get_cart_items()
            return render_template('order_summary.html', cart=cart, checkout=cd)

    return render_template('checkout_details.html', form=form)

@app.route('/checkout', methods=['POST'])
def order_summary():
    if request.method == 'POST':
        cart = shoppingcart.get_cart_items()

        if shoppingcart.cart_distinct_item_count() != 0:

            ordered_id = shoppingcart.genrate_order_id()
            total_products = shoppingcart.cart_distinct_item_count()
            total_amount = shoppingcart.get_total_amount()
            name = session['details']['name']
            address = session['details']['address']
            phone = session['details']['phone']
            email = session['details']['email']
            date = datetime.date.today()
            order_id = OrderId(order_id=ordered_id, buyer_name=name, buyer_address=address, phone=phone, email=email, date=date, total_products=total_products)
            db.session.add(order_id)
            db.session.commit()

            for item in cart:
                order = Ordered(name=item.products.name, amount=item.products.price, quantity=item.quantity, order_id=ordered_id)
                db.session.add(order)
                db.session.delete(item)
                db.session.commit()

            session.pop('details', None)
            id = OrderId.query.filter_by(order_id=ordered_id).first()
            product_id = Ordered.query.filter_by(order_id=ordered_id)

            order_email([id.email], id, product_id)
            return render_template('thank_you.html')

        else:
            flash('Your Cart is Empty.')
            return redirect(url_for('index'))

    return redirect(url_for('checkout_details'))