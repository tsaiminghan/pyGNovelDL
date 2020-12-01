import re
import urllib3
from collections import OrderedDict
from bs4 import BeautifulSoup
from urllib import parse
from ..settings import GLOBAL
from ..convert import STConvert, HtmlRemove
from ..download import download, set_charset, State

NAME = '範例'
NETLOC = 'www.sample.net'
REGEX = f'(?<={NETLOC}/)([^/]+)'
_NA = 'NA'
OPTIONS = {
    'download': {},
    'encoding': 'gbk',
}


def gen(title, href, chapter='', state=State.UNSET):
    """
    url: this is a list
    """
    return locals()


class NovelDL(object):
    netloc = NETLOC
    regex = REGEX
    options = {}
    _author = _NA
    _title = _NA
    _timestamp = '0000-00-00'

    def __init__(self, url):
        self.toc_url = self.parse_toc_url(url)
        options = OPTIONS.copy()
        options.update(self.options)
        self.options = options

        if not options['download'].get('verify', True):
            # disable warnings for verify=False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(1)
        return f'{scheme}://{self.netloc}/{book_id}/'

    @property
    def chap_url(self):
        return self.toc_url

    def set(self, book):
        self.book = book

    def download(self, url, **kwargs):
        self.pre_dl_option = kwargs
        kwargs.update(self.options.get('download', {}))
        ok, r = download(url, **kwargs)
        if ok:
            if encoding := self.options.get('encoding'):
                r.encoding = encoding
        return ok, r

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', id='list')

    @staticmethod
    def next_page(text):
        return None

    def key(self, url):
        return self.file_name(url).split('.')[0]

    def file_name(self, url):
        return url[len(self.chap_url):]

    def _filter_href(self, soup):
        div_list = self.chapters_filter(soup)
        all_chaps = div_list.find_all('a')
        result = {}
        for chap in all_chaps:
            url = parse.urljoin(self.chap_url, chap['href'])
            key = self.key(url)
            if key in result:
                del result[key]
            title = str(chap.string).strip()
            result[key] = gen(title, [url])
        return result

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(id='content')))

    def analysis(self, **kwargs):
        convert = STConvert.get_instance()
        ok, r = self.download(self.toc_url, **kwargs)
        if ok:
            soup = BeautifulSoup(convert(r.text), 'lxml')
            self.find_author(soup)
            self.find_title(soup)
            self.find_timestamp(soup)
            return ok, self._filter_href(soup)
        return ok, None

    def dl_chapter(self, key, **kwargs):
        item = self.book.chapters.get(key)
        content_file = self.book.content_file(key)
        if content_file.exists():
            ok = State.CONTENT_EXIST
        else:
            convert = STConvert.get_instance()
            url0 = item['href'][0]
            url = url0
            texts = ''
            ok = State.FAIL
            while url:
                if url not in item['href']:
                    item['href'].append(url)

                name = self.file_name(url)
                raw_file = self.book.raw_file(name)
                if raw_file.exists():
                    ok = State.RAW_EXIST
                    text = raw_file.read_text(encoding='utf-8')
                else:
                    ok, r = self.download(url, **kwargs)
                    if ok:
                        text = r.text
                        self.book.write_raw(name, set_charset(text))

                if ok:
                    url = self.next_page(text)
                    texts += self.content_filter(text)
                else:
                    break

            if ok:
                f = filter(None, map(str.strip, texts.split('\n')))
                '''line0 = next(f)
                texts = ('\n'.join(f))
                if not re.match(GLOBAL.regex, line0):
                    texts = '\n'.join([line0, texts])'''
                texts = ('\n'.join(f))
                self.book.write_content(key, convert(texts))
                ok = State.CONTENT_EXIST

        item['state'] = int(ok)
        return ok

    def find_author(self, soup):
        self._author = soup.find('meta', property='og:novel:author')['content']

    def find_title(self, soup):
        self._title = soup.find('meta', property='og:novel:book_name')['content']

    def find_timestamp(self, soup):
        self._timestamp = soup.find('meta', property='og:novel:update_time')['content']

    @property
    def author(self):
        return self._author

    @property
    def title(self):
        return self._title

    @property
    def timestamp(self):
        return self._timestamp
