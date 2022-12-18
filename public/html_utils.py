import re

class HtmlUtils():

    @staticmethod
    def remove_html_tags(content):
        cleanr = re.compile('<.*?>')
        clean_text = re.sub(cleanr, '', content)
        
        return clean_text

    @staticmethod    
    def remove_hashtag(content):
        hashtag_pattern = re.compile(r"#(.*)[\s]{0,1}", flags=re.UNICODE)
        cleaned_content = hashtag_pattern.sub(r' ', content)

        return cleaned_content