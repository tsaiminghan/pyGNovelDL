from shutil import rmtree
from ._sample import Command as Base
from ..settings import BOOKS
from ..book import Book


NAME = 'remove'


class Command(Base):
    """
Usage: n remove <id1> [<id2>...]
    use the list command to get id of novel.
    and then remove it by id.
    e.g.
      n remove 0
      n r 0 1 2"""
    name = NAME

    @staticmethod
    def remove(key=None, *, toc_url=None):
        if key:
            d = BOOKS[key]
            book = Book(d['toc_url'])
            BOOKS.remove(id=key)
        else:
            book = Book(toc_url)
            BOOKS.remove(toc_url=toc_url)
        rmtree(book.book_path, ignore_errors=True)
        print(f'remove {book.book_path}')
        try:
            book.book_path.parent.rmdir()
        except OSError:
            pass

    def __call__(self, *args, **kwargs):
        dirty = False
        for key in args:
            if BOOKS.get(key):
                self.remove(key)
                dirty = True
            else:
                print(f'unknown id {key}')

        if dirty:
            BOOKS.sort()
            BOOKS.dump()
