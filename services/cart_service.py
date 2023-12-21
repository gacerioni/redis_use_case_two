import json
from models.cart import ShoppingCart


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
        return all_carts