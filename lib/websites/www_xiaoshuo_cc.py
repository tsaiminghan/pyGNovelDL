import re
from ._sample import NovelDL as Base

NAME = '項點'
NETLOC = 'www.xiaoshuo.cc'
REGEX = f'(?<={NETLOC}/)([^/]+)'

OPTIONS = {
    'debug': False
}

# OK in 2021/06/06
# http://www.xiaoshuo.cc/27_27766/
# http://www.xiaoshuo.cc/27_27766/18335055.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    option = OPTIONS

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='listmain')



