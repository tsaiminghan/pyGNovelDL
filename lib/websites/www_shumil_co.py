import re
from bs4 import BeautifulSoup
from ._sample import NovelDL as Base

NAME = '書迷樓'
NETLOC = 'www.shumil.co'
REGEX = f'(?<={NETLOC}/)([^/]+)'


# OK in 2020/10/09
# https://www.shumil.co/jiuxingbatijue/
# https://www.shumil.co/jiuxingbatijue/27059145.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    @staticmethod
    def chapters_filter(soup):
        return soup.find('ul')

    @staticmethod
    def content_filter(text):
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.find(id='content')
        for key in ['div', 'a', 'center', 'b']:
            for i in tag.select(key):
                i.extract()
        return tag.get_text()

    def find_title(self, soup):
        self._title = soup.find(class_='tit').find('b').text

    def find_author(self, soup):
        self._author = re.search(r'(?<=作者:).+', soup.get_text()).group().strip()

    def find_timestamp(self, soup):
        # not support
        pass
