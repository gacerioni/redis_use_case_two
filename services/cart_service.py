import json
import logging
import os
import config
import redis

from models.cart import ShoppingCart
from services.skuitem_service import SKUService
from services.user_service import UserService

# GABS HACK TO AVOID CIRCULAR DEPENDENCY - I PREFER FASTAPI SOMETIMES
REDIS_HOST_OSS = os.getenv('REDIS_HOST_OSS', config.DEFAULT_REDIS_HOST_OSS)
REDIS_PORT_OSS = os.getenv('REDIS_PORT_OSS', config.DEFAULT_REDIS_PORT_OSS)
# Initialize Redis Connection
redis_conn = redis.Redis(host=REDIS_HOST_OSS, port=REDIS_PORT_OSS, db=0)
# Initialize SKU Service
sku_service = SKUService(redis_conn)
# Initialize User Service - for carts life quality improvement by Gabs
user_service = UserService(redis_conn)


class CartService:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def save_cart(self, cart):
        cart_key = f"cart:{cart.user_id}"
        cart_data = json.dumps(cart.get_items())
        self.redis_conn.set(cart_key, cart_data)

    def get_cart(self, user_id):
        cart_key = f"cart:{user_id}"
        cart_json = self.redis_conn.get(cart_key)
        if cart_json:
            items = json.loads(cart_json)
            cart = ShoppingCart(user_id)
            for sku_id, quantity in items.items():
                cart.add_item(sku_id, quantity)
            return cart
        return ShoppingCart(user_id)  # Return empty cart if none exists

    def add_item_to_cart(self, user_id, sku_id, quantity):
        cart = self.get_cart(user_id)
        cart.add_item(sku_id, quantity)
        self.save_cart(cart)

    def remove_item_from_cart(self, user_id, sku_id, quantity):
        cart = self.get_cart(user_id)
        cart.remove_item(sku_id, quantity)
        self.save_cart(cart)

    def get_all_carts(self):
        cart_keys = self.redis_conn.keys('cart:*')
        all_carts = {}
        for key in cart_keys:
            user_id = key.decode().split(':')[1]
            cart_json = self.redis_conn.get(key)
            if cart_json:
                items = json.loads(cart_json)
                cart = ShoppingCart(user_id)
                for sku_id, quantity in items.items():
                    cart.add_item(sku_id, quantity)
                all_carts[user_id] = cart.get_items()
        print("ALL CARTS: {}".format(str(all_carts)))
        return all_carts

    def get_cart_details(self, user_id):
        # Fetch the cart
        cart = self.get_cart(user_id)

        user = user_service.get_user(user_id)

        # Prepare cart details
        cart_details = {
            'user': {'id': user_id, 'username': user['username']},  # Use dictionary access
            'items': []
        }

        for sku_id, quantity in cart.items.items():
            sku = sku_service.get_sku(sku_id)  # Fetch SKU details
            cart_details['items'].append({
                'sku_id': sku_id,
                'name': sku.name,
                'quantity': quantity
            })

        return cart_details