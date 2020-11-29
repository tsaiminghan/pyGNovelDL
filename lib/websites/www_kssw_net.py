from bs4 import BeautifulSoup
from ._sample import NovelDL as Base
from ..convert import HtmlRemove

NAME = '看書小說'
NETLOC = 'www.kssw.net'
REGEX = f'(?<={NETLOC}/)(book/[^/]+)'

# OK in 2020/11/29
# http://www.kssw.net/book/7760/
# http://www.kssw.net/book/7760/9128478.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='mulu')

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        return handle(str(soup.find(class_='yd_text2')))

