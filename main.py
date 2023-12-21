import redis
from flask import Flask, render_template, request, redirect, url_for, flash

from models.skuitem import SKU
from models.user import User

import os

from dotenv import load_dotenv
import config
import logging

from services import user_service
from services.cart_service import CartService
from services.user_service import UserService
from services.skuitem_service import SKUService

# Load environment variables from .env file
load_dotenv()

# Get Redis host and port from environment variables or use fallbacks
REDIS_HOST_OSS = os.getenv('REDIS_HOST_OSS', config.DEFAULT_REDIS_HOST_OSS)
REDIS_PORT_OSS = os.getenv('REDIS_PORT_OSS', config.DEFAULT_REDIS_PORT_OSS)
REDIS_HOST_ENTERPRISE = os.getenv('REDIS_HOST_ENTERPRISE', config.DEFAULT_REDIS_HOST_ENTERPRISE)
REDIS_PORT_ENTERPRISE = os.getenv('REDIS_PORT_ENTERPRISE', config.DEFAULT_REDIS_PORT_ENTERPRISE)

# Gabs Logger configs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Define log format
log_format = "%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"  # Define date format

# GABS -  console handler and formatter
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(log_format, datefmt=date_format)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)

app = Flask(__name__, template_folder='templates', static_folder='static')
# Set a secret key for the application
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')

# Initialize Redis Connection
redis_conn = redis.Redis(host=REDIS_HOST_OSS, port=REDIS_PORT_OSS, db=0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    user_service_obj = UserService(redis_conn)

    if request.method == 'POST':
        # user_id = request.form['user_id']
        username = request.form['username']
        email = request.form['email']
        country = request.form['country']

        # Create a User instance - None will force the Svc to generate a UUID GABS
        new_user = User(None, username, email, country)

        # Save user to Redis using the UserService
        user_id = user_service_obj.save_user(new_user)

        flash(f'User created successfully with ID: {user_id}')
        return redirect(url_for('index'))  # Redirect to index or another appropriate page

    return render_template('create_user.html')


@app.route('/users')
def users():
    user_service_obj = UserService(redis_conn)

    users_list = user_service_obj.get_all_users()
    return render_template('users.html', users=users_list)


# Initialize SKU Service
sku_service = SKUService(redis_conn)


@app.route('/add_sku', methods=['GET', 'POST'])
def add_sku():
    if request.method == 'POST':
        sku_id = request.form['sku_id']
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        image_url = request.form['image_url']

        new_sku = SKU(sku_id, name, price, description, image_url)
        sku_service.add_sku(new_sku)

        flash('SKU added successfully!')
        return redirect(url_for('index'))

    return render_template('add_sku.html')


@app.route('/skus')
def skus():
    all_skus = sku_service.get_all_skus()
    return render_template('skus.html', skus=all_skus)


# Initialize Cart Service
cart_service = CartService(redis_conn)


@app.route('/add_to_cart')
def add_to_cart_form():
    user_service = UserService(redis_conn)
    all_users = user_service.get_all_users()
    all_skus = sku_service.get_all_skus()
    logger.info("All Users: {0}".format(all_users))
    logger.info("All SKUs: {0}".format(all_skus))
    return render_template('add_to_cart.html', users=all_users, skus=all_skus)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user_id = request.form['user_id']
    sku_id = request.form['sku_id']
    quantity = int(request.form['quantity'])

    cart_service.add_item_to_cart(user_id, sku_id, quantity)

    flash('Item added to cart successfully!')
    return redirect(url_for('view_cart', user_id=user_id))


@app.route('/view_cart/<user_id>')
def view_cart(user_id):
    cart = cart_service.get_cart(user_id)
    return render_template('view_cart.html', cart=cart, user_id=user_id)


@app.route('/view_carts')
def view_carts():
    all_carts = cart_service.get_all_carts()
    return render_template('view_carts.html', all_carts=all_carts)


if __name__ == '__main__':
    logger.info("Starting Gabs Flask server...")
    logger.info(os.getcwd())
    app.run(debug=True, host='0.0.0.0', port=5000)
