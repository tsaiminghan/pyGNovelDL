import webbrowser
from ._sample import Command as Base
from ..settings import BOOKS
from ..book import Book

NAME = 'folder'


class Command(Base):
    """
n browser <id>
    open the book folder."""
    name = NAME

    @staticmethod
    def open(url):
        book = Book(url)
        webbrowser.open(f'file:///{book.book_path}')

    def __call__(self, *args, **kwargs):
        for key in args:
            if d := BOOKS.get(key):
                self.open(d['toc_url'])
            else:
                print(f'unknown id {key}')

