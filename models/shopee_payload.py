import time
import json
import hmac
import hashlib

class ShopeePayload:
    SHOP_ID = 159834670
    PARTNER_ID = 843663
    SECRET_KEY = '6b353f3a6e25b47f33a7125b1c50c1bd3d96e5d079ca3051a2337e4074160578'
    UNLIST_URL = 'https://partner.shopeemobile.com/api/v1/items/unlist'
    UPDATE_STOCK_URL = 'https://partner.shopeemobile.com/api/v1/items/update_stock'
    GET_CATEGORIES_URL = 'https://partner.shopeemobile.com/api/v1/item/categories/get'
    GET_ATTRIBUTES_URL = 'https://partner.shopeemobile.com/api/v1/item/attributes/get'
    GET_ITEM_DETAIL_URL = 'https://partner.shopeemobile.com/api/v1/item/get'
    ADD_ITEM_URL = 'https://partner.shopeemobile.com/api/v1/item/add'

    def __init__(self):
        self.partner_id = ShopeePayload.PARTNER_ID
        self.shopid = ShopeePayload.SHOP_ID

    def get_default_body(self):
        return {
            'partner_id': self.partner_id,
            'shopid': self.shopid,
            'timestamp': self.get_timestamp()
        }

    def get_headers(self, url, body):
        return {
            'Content-Type' : 'application/json',
            'Authorization' : self.sign(url, json.dumps(body))
        }

    def sign(self, url, body):
        bs = url + "|" + body
        dig = hmac.new(ShopeePayload.SECRET_KEY.encode(), msg=bs.encode(),
                       digestmod=hashlib.sha256).hexdigest()
        return dig

    def get_timestamp(self):
        timestamp = int(time.time())
        return timestamp
