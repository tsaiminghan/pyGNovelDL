from bs4 import BeautifulSoup
from ._sample import NovelDL as Base

NAME = '燃文小說'
NETLOC = 'www.ranwen.la'
REGEX = fr'(?<={NETLOC}/)(files/article/\d+/\d+)'

# OK in 2022/04/29
# https://www.ranwen.la/files/article/89/89698/
# https://www.ranwen.la/files/article/89/89698/99664594.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    @staticmethod
    def content_filter(text):
        content = BeautifulSoup(text, 'lxml').find(id='content')
        for tag in content.select('a, div'):
            tag.extract()
        return content.get_text()

