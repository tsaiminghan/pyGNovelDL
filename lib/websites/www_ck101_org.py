import re
from urllib import parse
from ._sample import NovelDL as Base

NAME = '卡提諾小說網'
NETLOC = 'www.ck101.org'
REGEX = fr'(?<={NETLOC}/)[^/]+/(\d+)'
OPTIONS = {
    'encoding': 'big5',
}

# OK in 2020/10/07
# https://www.ck101.org/book/367312.html
# https://www.ck101.org/0/367312/
# https://www.ck101.org/367/367312/65879547.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS
    chap_url = ''

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(1)
        self.timestamp_url =\
            f'{scheme}://{self.netloc}/modules/article/52mb.php?id={book_id}&uptime='
        self.chap_url = f'{scheme}://{self.netloc}/{book_id[:-3]}/{book_id}/'
        return f'{scheme}://{self.netloc}/0/{book_id}/'

    def chapters_filter(self, soup):
        return soup.find('div', class_='novel_list')

    def find_author(self, soup):
        self._author = soup.find('meta', attrs={'name': 'og:novel:author'})['content']

    def find_title(self, soup):
        self._title = soup.find('meta', attrs={'name': 'og:novel:book_name'})['content']

    def find_timestamp(self, soup):
        ok, r = self.download(self.timestamp_url, **self.pre_dl_option)
        if ok:
            self._timestamp = re.search(r'\d{4}-\d{1,2}-\d{1,2}', r.text).group()

