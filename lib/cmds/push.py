from subprocess import run, CREATE_NO_WINDOW
from pathlib import Path
from ._sample import Command as Base
from ..settings import GLOBAL, BOOKS
from ..book import Book
from .shell import mtptransferSample as Mtp

NAME = 'push'


class Command(Base):
    r"""
Usage n send <id>
  copy the epub to MTP device.
  e.g.
    n push 0

  required:
    need global settings, device and copyto of mtp
    device:
      the name of MTP device. ex. Pixel 3 XL
    copyto:
      the path we copy books to, use the internal storage.
      ex Download\aa\bb"""

    @staticmethod
    def push(url):
        ps1 = Path('tmp.ps1')
        heads = '''param([string]$deviceName = '{}',
          [System.IO.FileInfo]$copyFrom = '{}',
          [string]$copyTo = '{}')
          '''
        book = Book(url)
        epub = book.book_file('.epub')
        with ps1.open('w', encoding='utf-8') as f:
            f.write(u'\ufeff')  # Write window BOM
            f.write(heads.format(
                GLOBAL.mtp['device'],
                epub,
                GLOBAL.mtp['copyto'],
            ))
            f.write(Mtp.__doc__)
        cmd = f'powershell -ExecutionPolicy Bypass -file {ps1}'
        r = run(cmd, creationflags=CREATE_NO_WINDOW)
        ps1.unlink()
        return r.returncode

    def __call__(self, *args, **kwargs):

        for key in args:
            if d := BOOKS.get(key):
                self.push(d['toc_url'])
            else:
                print(f'unknown id {key}')
