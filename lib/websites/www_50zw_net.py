from bs4 import BeautifulSoup
from ._sample import NovelDL as Base

NAME = '武林中文網'
NETLOC = 'www.50zw.net'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# OK in 2020/10/08
# https://www.50zw.net/zw_117970/
# https://www.50zw.net/zw_117970/45099846.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    @staticmethod
    def chapters_filter(soup):
        return soup.find('div', class_='liebiao_bottom')

    @staticmethod
    def content_filter(text):
        soup = BeautifulSoup(text, 'lxml')
        text = soup.find(id='neirong').get_text()
        lst = []
        for line in filter(None, map(str.strip, text.split('\n'))):
            if '♂' not in line:
                lst.append(line)
        return '\n'.join(lst)
