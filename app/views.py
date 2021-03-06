from app import app, db, shoppingcart
from flask import render_template, redirect, url_for, flash, make_response, request, session
from flask.ext.login import login_required, login_user, logout_user, current_user
from models import Admin
from forms import AdminLoginForm, CategoryForm, ProductForm, SignupForm, UserLoginForm, QuantityForm, UserInfoForm, ChangePasswordForm, AddAccountForm
from models import Category, Product, User, Cart, Ordered, OrderId, UserInfo
import datetime
from email import signup, order_email, send_pwd_url
from math import isnan



# User Login and Home page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index/', methods=['GET', 'POST'])
def index():
    form = UserLoginForm()
    signup = SignupForm()
    count = shoppingcart.product_count()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.username.data).first()
        if form.validate_on_submit():
            if user:
                if user.check_password(form.password.data):
                    session['username'] = user.email
                    flash('login succesful','text-success')
                    resp = make_response(render_template('home.html', user=user, count=count, cart_view=True))
                    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
                    return resp
                    flash('Login not valid', 'text-danger')
            flash('Login not valid', 'text-danger')

    return render_template('home.html', form=form, count=count, signup_form=signup, cart_view=True)

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
    count = shoppingcart.product_count()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, name=form.full_name.data.title())
        db.session.add(user)
        userinfo = UserInfo(name=form.full_name.data, email=form.email.data, user_information=user)
        db.session.add(userinfo)
        db.session.commit()
        signup([form.email.data])
        flash('Thank you for signing up.', 'text-success')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form, count=count, cart_view=True)


# Catalog
@app.route('/catalog/', methods=['GET', 'POST'])
def catalog():
    count = shoppingcart.product_count()
    form = QuantityForm()
    if request.method == 'POST' and form.validate_on_submit():
        key = request.form['product_slug']
        product_id = Product.query.get(key)
        quantity = request.form['quantity']
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
    return render_template('catalog.html', categories=category, products=product, form=form, count=count, cart_view=True)

# Cart
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
                flash('quantity should be greater than or equal to 1.', 'text-danger')
            else:
                cart.quantity = quantity
            db.session.commit()
    total_amount = shoppingcart.get_total_amount()
    cart = shoppingcart.get_cart_items()
    product_no = shoppingcart.product_count()
    return render_template('cart.html', cart=cart, count=product_no, total=total_amount, cart_view=True)


# Admin Login
@app.route('/admin/login/', methods=['GET', 'POST'])

def admin_login():
    count = shoppingcart.product_count()
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
    return render_template('admin-login.html', form=form, cart_view=True, count=count)

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
        db.session.commit()
        flash("category named "+ category.name + " is added to database.", 'text-success')
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
    flash("Category named "+ category.name +" is deleted.", 'text-success')
    return redirect(url_for('add_category'))

# Edit Category in Database
@app.route('/admin/category/edit/<int:pk>/', methods=['GET', 'POST'])
@login_required
def edit_category(pk):
    category= Category.query.get(pk)
    categories = Category.query.all()
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.add(category)
        db.session.commit()
        flash("Category edited", 'text-success')
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
        db.session.commit()
        flash(product.name + " added", 'text-success')
        return redirect(url_for('add_product'))
    product = Product.query.all()
    return render_template('admin-panel/product.html', form=form, product=product)

# Delete Product from Database
@app.route('/admin/product/delete/<int:pk>')
@login_required
def delete_product(pk):
    product = Product.query.get(pk)
    db.session.delete(product)
    db.session.commit()
    flash(product.name + " deleted", 'text-success')
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
        flash("Product saved.", 'text-success')
        return redirect(url_for("add_product"))
    return render_template("admin-panel/edit-product.html", product=product, products=products,
                           form=form, categories=categories)

# Sale list
@app.route('/admin/order_list')
@login_required
def orders():
    order = OrderId.query.all()
    return render_template('admin-panel/orders.html', orders=order)


# Getting specific order
@app.route('/admin/order/<int:pk>', methods=['GET', 'POST'])
@login_required
def specific_order(pk):
    order = OrderId.query.get(pk)
    ordered_products = Ordered.query.filter_by(order_id=order.order_id)
    return render_template('admin-panel/specific_order.html', order=order,products=ordered_products)

# change password of admin
@app.route('/admin/account/change_password/', methods=['GET','POST'])
@login_required
def change_admin_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        password = form.password.data
        current_user.password = current_user.set_password(password)
        db.session.commit()
        flash('password changed', 'text-success')
        return redirect(url_for('admin_base'))
    return render_template('admin-panel/change_password.html', form=form)

@app.route('/admin/account/add', methods=['GET', 'POST'])
@login_required
def add_account():
    form = AddAccountForm()
    if form.validate_on_submit():
        admin = Admin(username=form.email.data)
        db.session.add(admin)
        db.session.commit()
        admin1 = Admin.query.filter_by(email=form.email.data).first()
        send_pwd_url(admin1.email,admin1.id)
    return render_template('admin-panel/add-account.html', form=form)

'''User Account'''

#  Add User info
@app.route('/user/account/info', methods=['GET', 'POST'])
def user_info():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(email=username).first()
        userinfo = UserInfo.query.filter_by(user_id=user.id).first()
        form = UserInfoForm(obj=userinfo)
        if form.validate_on_submit():
            userinfo.address = form.address.data
            userinfo.city = form.city.data
            userinfo.phone = form.phone.data
            userinfo.pincode = form.pincode.data
            userinfo.state = form.pincode.data
            userinfo.name = form.name.data
            userinfo.email = form.email.data
            db.session.commit()
            flash('Information Saved.', 'text-success')
            return render_template('user-panel/user_info.html', user=user, form=form, cart_view=True)

        return render_template('user-panel/user_info.html', user=user, form=form, cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))
# User base
@app.route('/user/account')
def user_base():
    if 'username' in session:
        return render_template('user-panel/user_base.html', cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))
#  edit user info
@app.route('/user/account/edit')
def edit_info():
    if 'username' in session:
        form = UserInfoForm()
        return render_template('user-panel/edit_info.html', form=form, cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))

# user change password
@app.route('/user/account/change_password')
def edit_password():
    if 'username' in session:
        form = ChangePasswordForm()
        return render_template('user-panel/edit_password.html', form=form, cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))

# user order list
@app.route('/user/account/order')
def user_order():
    if 'username' in session:
        order = OrderId.query.filter_by(email=session['username'])
        return render_template('user-panel/user_order.html', order=order, cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))

# user's specific order details
@app.route('/user/account/order/<int:pk>', methods=['GET','POST'])
def specific_user_order(pk):
    if 'username' in session:
        orders = OrderId.query.get(pk)
        products = Ordered.query.filter_by(order_id=orders.order_id)
        return render_template('user-panel/user_specific_order.html', order=orders, products=products)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))

#change password
@app.route('/user/account/change_password/', methods=['GET','POST'])
def change_user_password():
    if 'username' in session:
        form = ChangePasswordForm()
        if form.validate_on_submit():
            password = form.password.data
            user = User.query.filter_by(email=session['username']).first()
            user.password = user.set_password(password)
            db.session.commit()
            flash('password changed', 'text-success')
            return redirect(url_for('user_base'))
        return render_template('user-panel/change_password.html', form=form, cart_view=True)
    else:
        flash('Please Login', 'text-danger')
        return redirect(url_for('index'))

'''Checkout'''

# Checkout Form wd
@app.route('/checkout/details', methods=['GET', 'POST'])
def checkout_details():
    if 'username' in session:
        user = User.query.filter_by(email=session['username']).first()
        userinfo = UserInfo.query.filter_by(user_id=user.id).first()
        form = UserInfoForm(obj=userinfo)
    else:
        form = UserInfoForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cd = {
                'name': form.name.data,
                'phone': request.form['phone'],
                'address': request.form['address']+', '+ request.form['city']+'-'+request.form['state']+' ('+request.form['pincode']+')',
                'email':request.form['email']
            }
            session['details'] = cd
            cart = shoppingcart.get_cart_items()
            total = shoppingcart.get_total_amount()
            return render_template('order_summary.html', cart=cart, checkout=cd, total=total)
        return 'not valid'
    return render_template('checkout_details.html', form=form)

@app.route('/checkout', methods=['POST'])
def order_summary():
    if request.method == 'POST':
        cart = shoppingcart.get_cart_items()

        if shoppingcart.product_count() != 0:

            ordered_id = shoppingcart.genrate_order_id()
            total_products = shoppingcart.product_count()
            total_amount = shoppingcart.get_total_amount()
            name = session['details']['name']
            address = session['details']['address']
            phone = session['details']['phone']
            email = session['details']['email']
            date = datetime.date.today()
            if 'username' in session:
                user = session['username']
            else:
                user = 'guest'
            order_id = OrderId(order_id=ordered_id, buyer_name=name, buyer_address=address, phone=phone, email=email, date=date, total_products=total_products, total_amount=total_amount, user=user)
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
            flash('Your Cart is Empty.', 'text-danger')
            return redirect(url_for('index'))

    return redirect(url_for('checkout_details'))