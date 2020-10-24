import re
from urllib import parse
from ._sample import NovelDL as Base

NAME = '愛奇文學'
NETLOC = 'www.iqiwx.com'
REGEX = fr'(?<={NETLOC}/book/)(\d+/)?(\d+)'

# OK in 2020/10/07
# https://www.iqiwx.com/book/100884.html
# https://www.iqiwx.com/book/100/100884/
# https://www.iqiwx.com/book/100/100884/30101435.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(2)
        return f'{scheme}://{self.netloc}/book/{book_id[:-3]}/{book_id}/'

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', id='readerlist')

    def find_author(self, soup):
        self._author = re.search(r'(?<=\?author=)[^"]+', str(soup)).group()

    def find_timestamp(self, soup):
        s = soup.find('div', id='smallcons').text
        self._timestamp = re.search(r'\d{4}-\d{1,2}-\d{1,2}', s).group()

    def find_title(self, soup):
        self._title = soup.find('h1').text

