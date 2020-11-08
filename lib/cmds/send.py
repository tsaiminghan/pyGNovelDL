import os
from ._device import Kindle
from ..settings import BOOKS
from ..book import Book
from ._sample import Command as Base
from ..util import copy

NAME = 'send'


class Command(Base):
    """
Usage n send <id1> [<id2>]...
  copy the mobi to Kindle device.
  e.g.
    n send 0
    n sen 0 1 2"""

    @staticmethod
    def kindle_exist():
        return Kindle().exist()

    @staticmethod
    def send2(url, callback):
        k = Kindle()
        book = Book(url)
        mobi = book.book_file('.mobi')
        filename = mobi.name
        target = os.path.join(k.drive, 'documents', filename)
        copy(mobi, target, callback=callback)

    @staticmethod
    def send(url):
        k = Kindle()
        book = Book(url)
        mobi = book.book_file('.mobi')
        if r := k.push(mobi):
            print(r)
            return r

    def __call__(self, *args, **kwargs):
        k = Kindle()
        if not k.exist():
            print('not find Kindle device')
            return

        for key in args:
            if d := BOOKS.get(key):
                self.send(d['toc_url'])
            else:
                print(f'unknown id {key}')
