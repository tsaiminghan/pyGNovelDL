from bs4 import BeautifulSoup
from urllib import parse
from ._sample import NovelDL as Base
from ._sample import gen
from ..convert import HtmlRemove

NAME = '落秋中文'
NETLOC = 'www.luoqiuzw.com'
REGEX = f'(?<={NETLOC}/)(book/[^/]+)'

OPTIONS = {
    'encoding': 'utf-8',
}

# OK in 2020/11/29
# https://www.luoqiuzw.com/book/291/
# https://www.luoqiuzw.com/book/291/71670943.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.find(id='content')
        result = ''
        for i in tag.select('p.content_detail'):
            result += str(i)
        return handle(result)

