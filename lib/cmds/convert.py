from ._sample import Command as Base
from ..settings import GLOBAL, BOOKS
from ..book import Book

NAME = 'convert'


class Command(Base):
    """
Usage: n convert <id> txt|aozora|epub|mobi
    txt      raw -> txt
    aozora   raw -> aozora txt
    epub     aozora txt -> epub
    mobi     epub -> mobi
    e.g.
      n c 0 t e"""
    name = NAME

    @staticmethod
    def convert(url, fmt):
        book = Book(url)
        return getattr(book, fmt)()

    def __call__(self, id, *args, **kwargs):
        trans = {
            't': 'txt',
            'a': 'aozora',
            'e': 'epub',
            'm': 'mobi',
            'k': 'kepub'
        }
        if d := BOOKS.get(id):
            book = Book(d['toc_url'])
            for arg in args:
                key = trans[arg[0]]
                if getattr(book, key)():
                    print('OK')
                else:
                    print('Fail')
        else:
            print(f'unknown id {id}')

