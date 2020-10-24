import re
from urllib import parse
from bs4 import BeautifulSoup
from ..convert import HtmlRemove
from ._sample import NovelDL as Base

NAME = '愛下電子書'
NETLOC = 'tw.aixdzs.com'
REGEX = fr'(?<={NETLOC}/)[^/]+/(\d+/\d+)'
OPTIONS = {
    'encoding': 'utf-8',
}

# OK in 2020/10/08
# https://tw.aixdzs.com/d/274/274774/
# https://tw.aixdzs.com/read/274/274774/
# https://tw.aixdzs.com/read/274/274774/p2.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS
    chap_url = ''

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(1)
        self.chap_url = f'{scheme}://{self.netloc}/read/{book_id}/p'
        return f'{scheme}://{self.netloc}/read/{book_id}/'

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='catalog')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(class_='content')))

    def find_title(self, soup):
        self._title = soup.find('h1').text

    def find_author(self, soup):
        self._author = soup.find('h2').find('span', itemprop='author').text

    def find_timestamp(self, soup):
        s = soup.find('h2').text
        self._timestamp = re.search(
            r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', s).group()
