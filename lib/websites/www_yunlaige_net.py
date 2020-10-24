import re
from bs4 import BeautifulSoup
from urllib import parse
from ._sample import NovelDL as Base, gen

NAME = '雲來閣'
NETLOC = 'www.yunlaige.net'
REGEX = fr'(?<={NETLOC}/)(book/[^/\.]+)'

# OK in 2020/10/19
# https://www.yunlaige.net/book/18123/
# https://www.yunlaige.net/book/18123/8559413.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def _filter_href(self, soup):
        result = {}
        for chap in soup.select(r'div.info-chapters.flex.flex-wrap a'):
            url = parse.urljoin(self.chap_url, chap['href'])
            key = self.key(url)
            if key in result:
                del result[key]
            title = chap['title']
            result[key] = gen(title, [url])
        return result

    @staticmethod
    def content_filter(text):
        soup = BeautifulSoup(text, 'lxml')
        return soup.find(class_='content').get_text()

