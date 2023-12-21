class ShoppingCart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = {}  # sku_id: quantity

    def add_item(self, sku_id, quantity):
        self.items[sku_id] = self.items.get(sku_id, 0) + quantity

    def remove_item(self, sku_id, quantity):
        if sku_id in self.items:
            self.items[sku_id] = max(0, self.items[sku_id] - quantity)
            if self.items[sku_id] == 0:
                del self.items[sku_id]

    def get_items(self):
        return self.items