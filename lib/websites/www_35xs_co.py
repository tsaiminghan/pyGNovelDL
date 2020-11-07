import re
from bs4 import BeautifulSoup
from ._sample import NovelDL as Base
from ..convert import HtmlRemove

NAME = '閃舞小說網'
NETLOC = 'www.35xs.co'
REGEX = f'(?<={NETLOC}/)(book/[^/]+)'

OPTIONS = {
    'encoding': 'utf-8',
}

# OK in 2020/11/07
# https://www.35xs.co/book/463056/
# https://www.35xs.co/book/463056/115790882.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS

    @staticmethod
    def chapters_filter(soup):
        return soup.find(class_='mulu_list')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(id='chaptercontent'))).replace(u'\ufeff', '')

