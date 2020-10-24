from bs4 import BeautifulSoup
from ._sample import NovelDL as Base
from ..convert import STConvert, HtmlRemove

NAME = '豬豬小說網'
NETLOC = 'www.zzdxss.com'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# OK in 2020/10/08
# https://www.zzdxss.com/mingmendiyishanhun/
# https://www.zzdxss.com/mingmendiyishanhun/12145842.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='list_box')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(class_='box_box')))

