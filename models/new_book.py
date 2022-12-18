import os
from .product import Product
from public.image_utils import ImageUtils as img_utils
from public.html_utils import HtmlUtils as html_utils
from public.string_utils import StringUtils as string_utils

class NewBook(Product):
    BOOK_NAME_LENGHT_LIMIT = 45
    CONDITION = 'NEW'
    NEW_BOOK_DESCRIPTION_LIMIT = (Product.DESCRIPTION_LENGTH_LIMIT
                                    -len(Product.BASE_DESCRIPTION_BLUEPRINT)+50)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.condition = self.CONDITION
        self.title = self.generate_title()
        self.description = self.generate_description()

    def generate_title(self):
        title = self.item_name.strip()
        title = title if len(title) < self.BOOK_NAME_LENGHT_LIMIT else title[0:self.BOOK_NAME_LENGHT_LIMIT]

        if self.sale_disc:
            self.sale_disc = str(int(self.sale_disc)).strip('0')
            title = f'{title}[{self.sale_disc}折]'

        if len(title + self.prod_id) < self.TITLE_LENGTH_LIMIT:
            title += self.prod_id

        return title

    def generate_description(self):
        description =  self.BASE_DESCRIPTION_BLUEPRINT % (
                        html_utils.remove_html_tags(self.control_text_overflow(self.author_main)),
                        html_utils.remove_html_tags(self.control_text_overflow(self.pub_nm_main)),
                        html_utils.remove_html_tags(self.control_text_overflow(self.publish_date)),
                        self.control_text_overflow(self.isbn),
                        self.control_text_overflow(self.language),
                        self.control_text_overflow(self.binding_type),
                        self.format_int(self.pages),
                        self.format_int(self.list_price),
                        html_utils.remove_html_tags(self.control_text_overflow(self.prod_pf, self.NEW_BOOK_DESCRIPTION_LIMIT))
        )

        return string_utils.replace_urls(description[:self.DESCRIPTION_LENGTH_LIMIT], '')

    def set_images(self, binary_cover, img_id_list):
        self.images.append(self.process_cover(binary_cover))

        for img in img_id_list[:self.IMAGES_LIMIT-2]:
            self.images.append(self.TAAZE_IMAGE_URL.format(img, self.IMAGE_HEIGHT, self.IMAGE_WIDTH))

        self.images.extend(self.FILLER_IMAGES_URL_LIST)