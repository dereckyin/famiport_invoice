from PIL import Image, ImageChops
import tempfile

class ImageUtils():
    PNG_FORMAT = '.png'
    JPG_FORMAT = '.jpg'
    BMP_FORMAT = '.bmp'

    @staticmethod
    def get_image_size(img_data):
        img_tmp_file = tempfile.TemporaryFile()
        img_tmp_file.write(img_data)

        dimensions = None
        with Image.open(img_tmp_file) as img:
            dimensions = img.size

        return dimensions

    @staticmethod
    def get_resized_images(img, new_img_height):
        return None

    @staticmethod
    def save_binary_image(img, img_destination):
        with open(img_destination, 'wb') as img_file:
            img_file.write(img)
            
            return img_destination

    @staticmethod
    def combine_images(img_one_route, img_two_route, img_destination, img_height=None):
        foreground = Image.open(img_one_route).convert("RGBA")

        width = int(img_height / foreground.height * foreground.width)
        foreground = foreground.resize((width, img_height))

        blank_image = Image.new('RGBA', (img_height,img_height), (255, 255, 255))
        blank_image.paste(foreground, (int((img_height-foreground.width)/2),int((img_height-foreground.height)/2)), foreground)

        second_img = Image.open(img_two_route)
        blank_image.paste(second_img, (0,0), second_img)

        blank_image.save(img_destination)
        return img_destination

    @staticmethod
    def place_background(img_url, img_height):
        foreground = Image.open(img_url).convert("RGBA")

        width = int(img_height / foreground.height * foreground.width)
        foreground = foreground.resize((width, img_height))

        blank_image = Image.new('RGBA', (img_height,img_height), (255, 255, 255))
        blank_image.paste(foreground, (int((img_height-foreground.width)/2),int((img_height-foreground.height)/2)), foreground)
        blank_image.save(img_url)

        return img_url