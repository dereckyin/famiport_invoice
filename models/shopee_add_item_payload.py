import json
from .shopee_payload import ShopeePayload

class ShopeeAddItemPayload(ShopeePayload):

    def __init__(self, shopee, **data):
        super().__init__()
        self.category_id = data['category_id']
        self.name = data['item_name']
        self.description = data['description']
        self.price = data['sale_price'] if data['sale_price'] > 0 else data['list_price']
        self.stock = data['stock'] if data['stock'] < 6 else 5
        self.item_sku = data['item_sku']
        self.weight = data['weight']
        self.images = data['images']
        self.attributes = self.builder_attributes(attributes_resp = shopee.item.get_attributes(category_id=int(data['category_id'])),
                                                    brand_option = data['value'],
                                                    default_brand_option = "自有品牌")
        self.logistics = self.builder_logistics()
        self.condition = "NEW" if data['item_sku'][0:3] == '111' else "USED"
        self.timestamp = self.get_timestamp()

    def get_payload_headers(self):
        return self.get_headers(ShopeePayload.UPDATE_STOCK_URL, self.__dict__)

    def get_url(self):
        return ShopeePayload.ADD_ITEM_URL

    def get_payload(self):
        payload = self.__dict__
        return json.dumps(payload)

    def builder_attributes(self, attributes_resp, brand_option = None, default_brand_option = "自有品牌"):
        attributes = []

        # in case attributes response is not define in api response
        if attributes_resp.get("attributes"):

            for ele in attributes_resp.get("attributes"):
                if ele.get("is_mandatory") and ele.get("attribute_name")=='品牌':
                    attributes.append(
                        {
                            "attributes_id": ele.get("attribute_id"),
                            "value": brand_option if brand_option else default_brand_option
                        })
                elif ele.get("is_mandatory"):
                    attributes.append(
                        {
                            # checking the value if value can radom or set as " "
                            "attributes_id": ele.get("attribute_id"),
                            "value": ele.get("options")[0] if len(ele.get("options")) > 0 else " ",
                        })
                else:
                    pass
        else:
            return None

        return attributes

    def builder_logistics(self):
        logistics = [{'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30006, 'logistic_name': '全家'}, 
                    {'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30005, 'logistic_name': '7-11'},
                    {'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30007, 'logistic_name': '萊爾富'}]
        return logistics