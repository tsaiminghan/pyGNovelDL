import re
from ._sample import NovelDL as Base

NAME = '筆趣閣'
NETLOC = 'www.b5200.net'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# OK in 2020/10/08
# http://www.b5200.net/135_135194/
# http://www.b5200.net/135_135194/172497148.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def find_timestamp(self, soup):
        s = soup.find(id='info').text
        self._timestamp = re.search(r'\d{4}-\d{1,2}-\d{1,2}', s).group()

