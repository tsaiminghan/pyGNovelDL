from ._sample import Command as Base
from ..book import Book
from ..settings import GLOBAL, BOOKS
from ..download import proxies
from ..util import timelog
from .list import Command as List

NAME = 'download'


class Command(Base):
    """
Usage: n download <url>
      download book by url
      e.g.
        n download http://www.b5200.net/101_101696/
        n d http://www.b5200.net/101_101696/"""
    name = NAME

    @timelog(NAME)
    def __call__(self, url, *args, **kwargs):
        option = {}
        if GLOBAL.proxy['enable']:
            option['proxies'] = proxies(**GLOBAL.proxy)
        b = Book(url)
        if b.data:
            print('Book exists, please use update command')
            return
        if not b.analysis(**option):
            print('#### analysis fail')
            return

        List.print(BOOKS.find(toc_url=b.toc_url)[1])

        for key, v in b.chapters.items():
            print(f'--- {v["title"]}')
            ok = b.dl_chapter(key, **option)
            if not ok:
                print('#### download fail')
                return
        b.dump()
        for key in GLOBAL.convert:
            print(f'------ {key}')
            if not getattr(b, key)():
                print(f'#### fail to transfer {key}')
                break
