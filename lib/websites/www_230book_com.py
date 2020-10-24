import re
from urllib import parse
from ._sample import NovelDL as Base
from ._sample import gen

NAME = '頂點小說'
NETLOC = 'www.230book.com'
REGEX = fr'(?<={NETLOC}/)(book/\d+)'

# OK in 2020/10/09
# https://www.230book.com/book/15682/
# https://www.230book.com/book/15682/3943488.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def _filter_href(self, soup):
        result = {}
        for chap in soup.select('ul._chapter a'):
            url = parse.urljoin(self.chap_url, chap['href'])
            title = str(chap.string)
            result[self.key(url)] = gen(title, [url])
        return result

    def find_timestamp(self, soup):
        s = soup.find(id='info').text
        self._timestamp = re.search(
            r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', s).group()
