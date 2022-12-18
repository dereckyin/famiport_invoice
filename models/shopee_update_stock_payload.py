import json

from requests.api import head
from .shopee_payload import ShopeePayload

class ShopeeStockPayload(ShopeePayload):

    def __init__(self, item_id, stock):
        super().__init__()
        self.item_id = item_id
        self.stock = stock if stock < 6 else 5
        self.timestamp = self.get_timestamp()

    def get_payload_headers(self):
        return self.get_headers(ShopeePayload.UPDATE_STOCK_URL, self.__dict__)

    def get_url(self):
        return ShopeePayload.UPDATE_STOCK_URL

    def get_payload(self):
        payload = self.__dict__
        return json.dumps(payload)

