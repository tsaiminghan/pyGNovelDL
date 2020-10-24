import re
from bs4 import BeautifulSoup
from lxml import etree
from urllib import parse
from ._sample import NovelDL as Base
from ..convert import HtmlRemove

NAME = '完本神站'
NETLOC = 'www.xinwanben.com'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# OK in 2020/10/07
# https://www.xinwanben.com/21851/
# https://www.xinwanben.com/21851/13847349.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    @staticmethod
    def chapters_filter(soup):
        tag = soup.find('div', class_='chapter')
        for i in tag.select('div'):
            i.extract()
        return tag

    def next_page(self, text):
        try:
            html = etree.HTML(text)
            url = html.xpath('//span[text()="下一页"]')[0].xpath('../@href')[0]
            if '_' in url:
                return parse.urljoin(self.toc_url, url)
        except IndexError:
            pass

    @staticmethod
    def content_filter(text):
        handle = HtmlRemove.get_instance()
        soup = BeautifulSoup(text, 'lxml')
        tag = soup.find('div', class_='readerCon')
        for i in tag.select('a'):
            i.extract()
        text = handle(str(tag))
        lst = []
        for line in list(filter(None, map(str.strip, text.split('\n'))))[0:-1]:
            if '♂' not in line:
                lst.append(line)

        text = '\n'.join(lst)
        regex = '^.{0,4}最新章節.{0,4}前往.{0,4}完.{0,4}本.{0,4}神.{0,4}站.{0,4}$.'
        return re.sub(regex, '', text, flags=re.M + re.S)

    def find_author(self, soup):
        self._author = soup.find('div', class_='writer').text.strip()

    def find_title(self, soup):
        self._title = soup.find('div', class_='detailTitle').text.strip()

    def find_timestamp(self, soup):
        s = soup.find('div', class_='chapterTitle').text
        self._timestamp = re.search(r'\d{4}-\d{1,2}-\d{1,2}', s).group()
