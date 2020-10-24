from ._sample import Command as Base
from ..book import Book
from ..settings import GLOBAL, BOOKS
from ..download import proxies
from ..download import State
from ..util import timelog
from .list import Command as List

NAME = 'update'


class Command(Base):
    """
Usage: n update [<id>...]

      update ids of books
      e.g.
        n update 0
        n u 0 1

      update all of books
      e.g.
        n update
        n u"""
    name = NAME

    def __init__(self):
        option = {}
        if GLOBAL.proxy['enable']:
            option['proxies'] = proxies(**GLOBAL.proxy)
        self.option = option

    def update(self, book_id, toc_url):
        dirty = False
        b = Book(toc_url)
        if not b.analysis(**self.option):
            print('#### analysis fail')
            return
        List.print(BOOKS[book_id])

        for key, v in b.chapters.items():
            ok = b.dl_chapter(key, **self.option)
            if ok == State.FAIL:
                print('#### download fail')
                return
            if ok != State.CONTENT_EXIST:
                dirty = True
                print(f'--- {v["title"]}')
        b.dump()

        if not dirty:
            return

        for key in GLOBAL.convert:
            print(f'------ {key}')
            if not getattr(b, key)():
                print(f'#### fail to transfer {key}')
                break

    @timelog(NAME)
    def __call__(self, *args, **kwargs):
        if args:
            for arg in args:
                if d := BOOKS.get(arg):
                    self.update(arg, d['toc_url'])
                else:
                    print(f'unknown id {arg}')
        else:
            for k, d in BOOKS.items():
                self.update(k, d['toc_url'])
