
class ImageError(Exception):
    pass

class NoImagesException(ImageError):
    pass

class ImageTooSmallException(ImageError):
    pass

class ImageUploadException(ImageError):
    pass