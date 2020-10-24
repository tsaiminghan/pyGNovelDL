import re
from lxml import etree
from bs4 import BeautifulSoup
from urllib import parse
from ._sample import NovelDL as Base
from ..convert import HtmlRemove

# OK in 2020/10/07
# https://www.xssilu.com/159417/?btwaf=54192000
# https://www.xssilu.com/159417/
# https://www.xssilu.com/159417/61939683.html

NAME = '絲路文學'
NETLOC = 'www.xssilu.com'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# window.location.href
regex = r'(?<=\?btwaf=)(\d+)'


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def download(self, url, **kwargs):
        ok, r = super().download(url, **kwargs)
        if ok:
            ret = re.search(regex, r.text)
            if ret:
                new_url = f'{url}?btwaf={ret.group()}'
                ok, r = super().download(new_url, **kwargs)
        return ok, r

    def next_page(self, text):
        try:
            html = etree.HTML(text)
            href = html.xpath('//a[text()="下一章"]/@href')[0]
            if '_' in href:
                return parse.urljoin(self.toc_url, href)
        except Exception as e:
            print(e)

    @staticmethod
    def chapters_filter(soup):
        return soup.find('ul', class_='chapters')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.find(id='content')
        for i in tag.select('div'):
            i.extract()
        return handle(str(tag))
