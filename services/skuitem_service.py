import json
from models.skuitem import SKU


class SKUService:
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def add_sku(self, sku):
        sku_key = f"sku:{sku.sku_id}"
        sku_data = {
            'name': sku.name,
            'price': sku.price,
            'description': sku.description,
            'image_url': sku.image_url
        }
        sku_json = json.dumps(sku_data)
        self.redis_conn.set(sku_key, sku_json)

    def get_sku(self, sku_id):
        sku_key = f"sku:{sku_id}"
        sku_json = self.redis_conn.get(sku_key)
        if sku_json:
            sku_data = json.loads(sku_json)
            return SKU(sku_id, sku_data['name'], sku_data['price'], sku_data['description'], sku_data['image_url'])
        return None

    def get_all_skus(self):
        sku_keys = self.redis_conn.keys('sku:*')
        skus = []
        for key in sku_keys:
            sku_json = self.redis_conn.get(key)
            sku_data = json.loads(sku_json)
            sku_id = key.decode().split(':')[1]
            skus.append(SKU(sku_id, sku_data['name'], sku_data['price'], sku_data['description'], sku_data['image_url']))
        return skus
