from .category import Category

class YahooCategory(Category):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_images(self, binary_cover, img_id_list):
        pass

    def generate_title(self):
        pass

    def generate_description(self):
        pass