import re
from bs4 import BeautifulSoup
from ..convert import HtmlRemove
from urllib import parse
from ._sample import NovelDL as Base

NAME = '齋書苑'
NETLOC = 'www.zhaishuyuan.com'
REGEX = fr'(?<={NETLOC}/)[^/]+/(\d+)'

# OK in 2020/10/08
# https://www.zhaishuyuan.com/book/11303
# https://www.zhaishuyuan.com/read/11303
# https://www.zhaishuyuan.com/chapter/11303/23706624


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    chap_url = ''

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(1)
        self.chap_url = f'{scheme}://{self.netloc}/chapter/{book_id}/'
        return f'{scheme}://{self.netloc}/read/{book_id}/'

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', id='readerlist')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.find(id='content')
        for i in tag.select('div'):
            i.extract()
        return handle(str(tag))

