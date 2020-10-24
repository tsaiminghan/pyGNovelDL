import re
from urllib import parse
from ._sample import NovelDL as Base

NAME = '67書吧'
NETLOC = 'www.67shu.net'
REGEX = fr'(?<={NETLOC}/)(\d+/|book_)?(\d+)/'

# OK in 2020/10/07
# https://www.67shu.net/book_112092/
# https://www.67shu.net/book_112092/41713611.html
# https://www.67shu.net/112/112092/


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def parse_toc_url(self, url):
        scheme = parse.urlparse(url).scheme
        book_id = re.search(self.regex, url).group(2)
        return f'{scheme}://{self.netloc}/book_{book_id}/'

