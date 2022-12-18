import os
import cx_Oracle
import multiprocessing
from multiprocessing import Process
from abc import ABC, abstractmethod
from public.image_utils import ImageUtils as img_utils
from public.html_utils import HtmlUtils as html_utils

class Product(ABC):    
    TITLE_LENGTH_LIMIT = 60
    DESCRIPTION_LENGTH_LIMIT = 3000
    IMAGE_HEIGHT = 800
    IMAGE_WIDTH = 800
    IMAGES_LIMIT = 9
    COVER_URL_LIST = [r'\\192.168.100.48\shopee_img\\', r'\\192.168.100.58\shopee_img\\']
    # COVER_URL_LIST = [r'\\192.168.100.58\shopee_img\\']
    TAAZE_IMAGE_URL = 'https://media.taaze.tw/showThumbnailByPk.html?sc={}&height={}&width={}'
    COVER_IMAGE_URL = 'https://media.taaze.tw/ShopeeImg/{}.png'
    FILLER_IMAGES_URL_LIST = [
        'https://s-cf-tw.shopeesz.com/file/6c16f345918985e4fc77a0b917ac5844',
        'https://s-cf-tw.shopeesz.com/file/1d670075b591a3b09254d416064599c4',
        'https://s-cf-tw.shopeesz.com/file/a26762de9d1c0b3fbf3f323dcc53db48'
    ]
    BASE_DESCRIPTION_BLUEPRINT = """商品資料
                作者：%s
                出版社：%s
                出版日期：%s
                ISBN/ISSN：%s
                語言：%s
                裝訂方式：%s
                頁數：%s
                原價：%s
                ------------------------------------------------------------------------

內容簡介
%s"""

    def __init__(self, **kwargs):
        self.item_id = self.get_value(kwargs, 'ITEM_ID', None)
        self.item_name = self.get_value(kwargs, 'TITLE_MAIN', None)
        self.isbn = self.get_value(kwargs, 'ISBN', None)
        self.ean = self.get_value(kwargs, 'EANCODE', None)
        self.serial_no = self.get_value(kwargs, 'PROD_SERIALNO', None)
        self.prod_id = self.get_value(kwargs, 'PROD_ID', None)
        self.sup_name = self.get_value(kwargs, 'SUP_NM_MAIN', None)
        self.author_main = self.get_value(kwargs, 'AUTHOR_MAIN', None)
        self.author_next = self.get_value(kwargs, 'AUTHOR_NEXT', None)
        self.translator = self.get_value(kwargs, 'TRANSLATOR', None)
        self.editor = self.get_value(kwargs, 'EDITOR', None)
        self.printer = self.get_value(kwargs, 'PAINTER', None)
        self.pub_nm_main = self.get_value(kwargs, 'PUB_NM_MAIN', None)
        self.pub_nm_next = self.get_value(kwargs, 'PUB_NM_NEXT', None)
        self.publish_date = self.get_value(kwargs, 'PUBLISH_DATE', None)
        self.list_price = self.get_value(kwargs, 'LIST_PRICE', None)
        self.special_price = self.get_value(kwargs, 'SPECIAL_PRICE', None)
        self.language = self.get_value(kwargs, 'LANGUAGE', None)
        self.series4pub_nm = self.get_value(kwargs, 'SERIES4PUB_NM', None)
        self.prod_pf = self.get_value(kwargs, 'PROD_PF', '')
        self.author_pf = self.get_value(kwargs, 'AUTHOR_PF', '')
        self.translator_pf = self.get_value(kwargs, 'TRANSLATOR_PF', '')
        self.catalogue = self.get_value(kwargs, 'CATALOGUE', None)
        self.preface = self.get_value(kwargs, 'PREFACE', '')
        self.viewdata = self.get_value(kwargs, 'VIEWDATA', None)
        self.pages = self.get_value(kwargs, 'PAGES', 0)
        self.book_size = self.get_value(kwargs, 'BOOK_SIZE', None)
        self.weight = self.get_value(kwargs, 'WEIGHT', 0.2)
        self.size_l = self.get_value(kwargs, 'SIZE_L', 0.0)
        self.size_w = self.get_value(kwargs, 'SIZE_W', 0.0)
        self.size_h = self.get_value(kwargs, 'SIZE_H', 0.0)
        self.binding_type = self.get_value(kwargs, 'BINDING_TYPE', None)
        self.printing = self.get_value(kwargs, 'PRINTING', None)
        self.country_nm_cn = self.get_value(kwargs, 'COUNTRY_NM_CN', None)
        self.org_flg = self.get_value(kwargs, 'ORG_FLG', None)
        self.retn_flg = self.get_value(kwargs, 'RETN_FLG', None)
        self.pur_tax = self.get_value(kwargs, 'PUR_TAX', None)
        self.pur_disc = self.get_value(kwargs, 'PUR_DISC', None)
        self.sale_price = self.get_value(kwargs, 'SALE_PRICE', None)
        self.sale_disc =self.get_value(kwargs, 'SALE_DISC', None)
        self.forsale_flg = self.get_value(kwargs, 'FORSALE_FLG', None)
        self.forsale = self.get_value(kwargs, 'FORSALE', None)
        self.out_of_print = self.get_value(kwargs, 'OUT_OF_PRINT', None)
        self.stk_sell_flg = self.get_value(kwargs, 'STK_SELL_FLG', None)
        self.sup_mode = self.get_value(kwargs, 'SUP_MODE', None)
        self.islimit_flg = self.get_value(kwargs, 'ISLIMIT_FLG', None)
        self.copyright = self.get_value(kwargs, 'COPYRIGHT', None)
        self.status_flg = self.get_value(kwargs, 'STATUS_FLG', None)
        self.media_rcm = self.get_value(kwargs, 'MEDIA_RCM', None)
        self.cat_nm = self.get_value(kwargs, 'CAT_NM', None)
        self.cat_id = self.get_value(kwargs, 'CAT_ID', None)
        self.stock = self.get_value(kwargs, 'VAL', 0)
        self.cat_nm = self.get_value(kwargs, 'CAT_NAME', None)
        self.prod_rank = self.get_value(kwargs, 'PROD_RANK', None)
        self.note = self.get_value(kwargs, 'NOTE', '')
        self.org_prod_id = self.get_value(kwargs, 'ORG_PROD_ID', None)
        self.pub_id = self.get_value(kwargs, 'PUB_ID', None)
        self.media_rcm = self.get_value(kwargs, 'MEDIA_RCM', None)
        self.pub_spe_nm = self.get_value(kwargs, 'PUB_SPE_NM', None)
        self.stock = self.get_stock(kwargs)
        self.price = self.get_product_price()
        self.logistics = self.get_logistics()
        self.shopee_cat_id = self.get_shopee_category()
        self.brand = self.get_brand()
        self.images = []

    def get_product_price(self):
        price = self.list_price if self.sale_price == 0 else self.sale_price
        
        return int(price)

    def get_stock(self, kwargs):
        stock = self.get_value(kwargs, 'VAL', 0)
        return stock if stock <= 4 else 5 

    def get_value(self, data, key, default_value=None):
        try:
            if data[key]:
                if type(data[key]) == cx_Oracle.LOB:
                    data[key] = data[key].read()

                return data[key]
            
            return default_value
        
        except KeyError:
            return default_value

    def control_text_overflow(self, text, max_length=DESCRIPTION_LENGTH_LIMIT):
        if not text:
            return ''
        
        return (text[0:max_length] + '..') if len(text) > max_length else text

    def format_int(self, value):
        if not value:
            return '0'

        return str(int(value))

    def get_brand(self):
        return self.pub_spe_nm if self.pub_spe_nm else self.pub_nm_main

    def get_logistics(self):
        return [
            {'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30006, 'logistic_name': '全家'},
            {'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30005, 'logistic_name': '7-11'},
            {'enabled': True, 'estimated_shipping_fee': 60.0, 'is_free': False, 'logistic_id': 30007, 'logistic_name': '萊爾富'}
        ]

    def get_shopee_category(self):
        cat_id = 24596                       # 其他

        if self.cat_nm is None:
            return cat_id
        
        if self.prod_id == "090303000000":       # 教科參考書
            cat_id = 24584
        if self.prod_id == "060900000000":       # 雜誌期刊
            cat_id = 24586
        if self.cat_nm.find("電腦") != -1:
            cat_id = 24600
        if self.cat_nm.find("華文文學") != -1 or self.cat_nm.find("世界文學") != -1 or self.cat_nm.find("類型文學") != -1:
            cat_id = 24588
        if self.cat_nm.find("旅遊") != -1:
            cat_id = 24590
        if self.cat_nm.find("政府考用") != -1 or self.cat_nm.find("教育") != -1:
            cat_id = 24584
        if self.cat_nm.find("漫畫") != -1:
            cat_id = 24594
        if self.cat_nm.find("宗教") != -1 or self.cat_nm.find("命理") != -1:
            cat_id = 24602
        if self.cat_nm.find("醫學保健") != -1:
            cat_id = 24604
        if self.cat_nm.find("少兒親子") != -1:
            cat_id = 24606
        if self.cat_nm.find("科學") != -1:
            cat_id = 24610
        if self.cat_nm.find("心理勵志") != -1:
            cat_id = 24619
        if self.cat_nm.find("傳記") != -1:
            cat_id = 24596
        if self.cat_nm.find("藝術") != -1 or self.cat_nm.find("建築設計") != -1:
            cat_id = 24608
        if self.cat_nm.find("自然") != -1 or self.cat_nm.find("科普") != -1:
            cat_id = 24610
        if self.cat_nm.find("歷史地理") != -1 or self.cat_nm.find("哲學宗教") != -1 or self.cat_nm.find("社會科學") != -1:
            cat_id = 24687
        if self.cat_nm.find("生活風格") != -1:
            cat_id = 24615
        if self.cat_nm.find("商業") != -1 or self.cat_nm.find("理財") != -1:
            cat_id = 24617
        if self.cat_nm.find("心理") != -1 or self.cat_nm.find("勵志") != -1:
            cat_id = 24619
        if self.cat_nm.find("語言") != -1:             # 語言與程式語言需要處理
            cat_id = 24592
        if self.cat_nm.find("電腦") != -1:
            cat_id = 24600
        if self.prod_rank == "限":
            cat_id = 24621

        return cat_id

    def save_and_set_background(self, binary_img, url):
        img_utils.save_binary_image(binary_img, url)
        img_utils.place_background(url, self.IMAGE_HEIGHT)

        return url

    def process_cover(self, binary_img):
        for url in self.COVER_URL_LIST:
            self.save_and_set_background(binary_img, os.path.join(url, self.prod_id + img_utils.PNG_FORMAT))

        return self.COVER_IMAGE_URL.format(self.prod_id)

    def set_shopee_images(self, shopee_img_list):
        self.shopee_images = shopee_img_list

    @abstractmethod
    def set_images(self, binary_cover, img_id_list):
        pass

    @abstractmethod
    def generate_title(self):
        pass

    @abstractmethod
    def generate_description(self):
        pass