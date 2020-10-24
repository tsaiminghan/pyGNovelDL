from bs4 import BeautifulSoup
from ._sample import NovelDL as Base
from ._sample import gen
from urllib import parse
from ..convert import STConvert, HtmlRemove

NAME = '起點中文網'
NETLOC = 'book.qidian.com'
REGEX = rf'(?<={NETLOC}/)([^/]+/\d+)'
OPTIONS = {
    'encoding': 'utf-8',
}

# OK in 2020/10/05
# https://book.qidian.com/info/1022893151


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS
    chap_url = 'https://read.qidian.com/chapter/'
    cate_url = 'https://book.qidian.com/ajax/book/category'

    def content_filter(self, text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(
            'div',
            class_='read-content j_readContent')))

    def _filter_href(self, dict_data):
        convert = STConvert.get_instance()
        result = {}
        data = dict_data['data']
        vs = data['vs']  # list
        for d in vs:
            chapter = convert(d['vN'])
            vip = d['vS']
            if vip:
                # skip vip chapter
                break

            for d2 in d['cs']:
                # the time of the last free chapter
                self._timestamp = d2['uT']
                url = parse.urljoin(self.chap_url, d2['cU'])
                result[self.key(url)] = gen(title=convert(d2['cN']),
                                            href=[url],
                                            chapter=chapter)
                if chapter:
                    chapter = ''
        return result

    def analysis(self, **kwargs):
        ok, r = self.download(self.toc_url, **kwargs)
        if ok:
            convert = STConvert.get_instance()
            cookie = r.cookies.get_dict()
            soup = BeautifulSoup(convert(r.text), 'lxml')
            self.find_author(soup)
            self.find_title(soup)

            params = dict(cookie)
            params['bookId'] = self.toc_url.split('/')[-2]

            ok, r = self.download(self.cate_url, params=params, **kwargs)
            if ok:
                return ok, self._filter_href(r.json())
        return ok, None

    def find_author(self, soup):
        self._author = soup.find('h1').find('a').text

    def find_title(self, soup):
        self._title = soup.find('h1').find('em').text
