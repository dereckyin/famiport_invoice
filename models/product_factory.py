from .product import Product
from .new_book import NewBook
from .used_book import UsedBook
from .department_product import DepartmentProduct
from .yahoo_category import YahooCategory

class ProductFactory():
    NEW_BOOK_ID = '111'
    USED_BOOK_ID = '113'

    @staticmethod
    def produce_item(**kwargs):
        item_type_id = kwargs['PROD_ID'][0:3]

        if item_type_id == ProductFactory.NEW_BOOK_ID:
            return NewBook(**kwargs)
        
        if item_type_id == ProductFactory.USED_BOOK_ID:
            return UsedBook(**kwargs)

        return DepartmentProduct(**kwargs)

    def category_item(**kwargs):
        return YahooCategory(**kwargs)