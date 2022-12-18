import os
from .product import Product
from public.image_utils import ImageUtils as img_utils
from public.html_utils import HtmlUtils as html_utils
from public.string_utils import StringUtils as string_utils

class UsedBook(Product):
    TAG_IMG_ROUTE = r'D:\shopee\images\\'
    CONDITION = 'USED'
    SECOND_HAND_NAME_LIMIT = 40
    SECOND_HAND_BOOK = '二手書'
    SECOND_HAND_DESCRIPTION = """二手書購物須知
1. 購買二手書時，請檢視商品書況或書況影片。
商品名稱後方編號為賣家來源。
2. 商品版權法律說明：TAAZE 讀冊生活單純提供網路二手書託售平台予消費者，並不涉入書本作者與原出版商間之任何糾紛；敬請各界鑒察。
3. 二手商品無法提供換貨服務，僅能辦理退貨。如須退貨，請保持該商品及其附件的完整性(包含書籍封底之TAAZE物流條碼)。若退回商品無法回復原狀者，可能影響退換貨權利之行使或須負擔部分費用。
4. 退換貨說明：二手書籍商品享有15天的商品猶豫期（含例假日）。若您欲辦理退貨，請於取得該商品15日內寄回。但以下幾種狀況不得辦理退貨：
a. 與書況影片相較有差異(撞損..)
b. 附件不符(原有含CD)
c. 物流條碼被撕除
訂購本商品前請務必詳閱退換貨原則。
5. 書況標定 : 二手書「書況」由讀冊生活統一標定，標準如下，下單前請先確認該商品書況，若下單則視為確認及同意書況。
a.全新：膠膜未拆，無瑕疵。
b.近全新：未包膜，翻閱痕跡不明顯，如實體賣場陳列販售之書籍。
c.良好：有使用痕跡，不如新書潔白、小範圍瑕疵，如摺角、碰撞、汙點或泛黃等。
"""
    USED_BOOK_DESCRIPTION_LIMIT = (Product.DESCRIPTION_LENGTH_LIMIT
                                    -len(Product.BASE_DESCRIPTION_BLUEPRINT)-200
                                    -len(SECOND_HAND_DESCRIPTION))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.condition = self.CONDITION
        self.title = self.generate_title()
        self.description = self.generate_description()

    def generate_title(self):
        item_name = self.item_name
        if len(item_name) > self.SECOND_HAND_NAME_LIMIT:
            item_name = item_name[:self.SECOND_HAND_NAME_LIMIT-1]

        title = f'{item_name}[{self.SECOND_HAND_BOOK}_{self.prod_rank}]{self.prod_id}'

        return title

    def generate_description(self):        
        description =  html_utils.remove_hashtag(
            (self.note + '\n' + self.BASE_DESCRIPTION_BLUEPRINT % (
                        html_utils.remove_html_tags(self.control_text_overflow(self.author_main)),
                        html_utils.remove_html_tags(self.control_text_overflow(self.pub_nm_main)),
                        html_utils.remove_html_tags(self.control_text_overflow(self.publish_date)),
                        self.control_text_overflow(self.isbn),
                        self.control_text_overflow(self.language),
                        self.control_text_overflow(self.binding_type),
                        self.format_int(self.pages),
                        self.format_int(self.list_price),
                        html_utils.remove_html_tags(self.control_text_overflow(self.prod_pf, self.USED_BOOK_DESCRIPTION_LIMIT))
                ) + '\n\n' + self.SECOND_HAND_DESCRIPTION)
             )

        return string_utils.replace_urls(description, '')

    def set_images(self, binary_cover, img_id_list):
        self.images.append(self.process_cover(binary_cover))

        for url in self.COVER_URL_LIST:
            img_path = os.path.join(url, self.prod_id + img_utils.PNG_FORMAT)
            img_utils.combine_images(img_path, 
                                      os.path.join(self.TAG_IMG_ROUTE, self.prod_rank + img_utils.PNG_FORMAT),
                                      img_path,
                                      self.IMAGE_HEIGHT)

        for img in img_id_list[:self.IMAGES_LIMIT-2]:
            self.images.append(self.TAAZE_IMAGE_URL.format(img, self.IMAGE_HEIGHT, self.IMAGE_WIDTH))

        self.images.extend(self.FILLER_IMAGES_URL_LIST)