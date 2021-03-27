import re
from urllib import parse
from collections import OrderedDict
from bs4 import BeautifulSoup
from ..convert import HtmlRemove
from ._sample import NovelDL as Base, gen

NAME = '繁體小說網'
NETLOC = 'www.twfanti.com'
REGEX = fr'(?<={NETLOC}/)(book/)?([^/\.]+)'

# OK in 2020/10/09
# https://www.twfanti.com/book/MoDaoShenTu7.html
# https://www.twfanti.com/MoDaoShenTu7/read_4180.html

OPTIONS = {
    'encoding': 'utf-8',
}


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS
    chap_url = ''

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(2)
        self.chap_url = f'{scheme}://{self.netloc}/{book_id}/read_'
        return f'{scheme}://{self.netloc}/book/{book_id}.html'

    def next_page(self, text):
        try:
            soup = BeautifulSoup(text, 'lxml')
            url = soup.find('a', class_='pt-nextchapter')['href']
            if 'p' in url.split('/')[-1]:
                return parse.urljoin(self.chap_url, url)
        except IndexError:
            pass

    def _filter_href(self, soup):
        result = {}
        for chap in soup.select(r'div.pt-chapter-cont-detail.full a'):
            url = parse.urljoin(self.chap_url, chap['href'])
            title = chap['title']
            result[self.key(url)] = gen(title, [url])
        return result

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        s = handle(str(soup.find(class_='size16 color5 pt-read-text')))
        regex = r'本章未完，請點擊下一頁繼續閱讀！ 第\d頁/共\d頁'
        return re.sub(regex, '', s)

    def find_timestamp(self, soup):
        self._timestamp = re.search(
            r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}',
            str(soup)).group()
