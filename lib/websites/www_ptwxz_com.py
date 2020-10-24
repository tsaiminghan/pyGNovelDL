import re
import urllib3
from urllib import parse
from bs4 import BeautifulSoup
from ._sample import NovelDL as Base
from ..convert import STConvert, HtmlRemove

NAME = '飄天文學網'
NETLOC = 'www.ptwxz.com'
REGEX = fr'(?<={NETLOC}/)[^/]+/(\d+/\d+)'
OPTIONS = {
    'download': {
        'verify': False
    },
}

# OK in 2020/10/07
# https://www.ptwxz.com/html/10/10231/
# https://www.ptwxz.com/html/10/10231/7267983.html
# https://www.ptwxz.com/bookinfo/10/10231.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS

    def parse_toc_url(self, url):
        # disable warnings for verify=False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(1)
        self.info_url = f'{scheme}://{self.netloc}/bookinfo/{book_id}.html'
        return f'{scheme}://{self.netloc}/html/{book_id}/'

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='centent')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        regex = '(?<=<br>)(.+?)</div>'
        return handle(re.search(regex, text, re.S).group(1))

    def find_author(self, soup):
        self._author = soup.find('meta', attrs={'name': 'author'})['content']

    def find_title(self, soup):
        convert = STConvert.get_instance()
        ok, r = self.download(self.info_url, **self.pre_dl_option)
        if ok:
            soup = BeautifulSoup(r.text, 'lxml')
            self._timestamp = re.search(r'\d{4}-\d{1,2}-\d{1,2}', soup.text).group()
            self._title = convert(soup.find('h1').text)

    def find_timestamp(self, soup):
        pass

