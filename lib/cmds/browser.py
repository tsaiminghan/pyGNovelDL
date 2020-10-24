import sys
import subprocess
import webbrowser
from ._sample import Command as Base
from ..settings import BOOKS

NAME = 'browser'


class Command(Base):
    """
n browser <id>
  open the book url."""
    name = NAME

    @staticmethod
    def open(url):
        if sys.platform == 'darwin':
            subprocess.Popen(['open', url])
        else:
            webbrowser.open_new_tab(url)

    def __call__(self, *args, **kwargs):
        for key in args:
            if d := BOOKS.get(key):
                url = d['toc_url']
                self.open(url)
            else:
                print(f'unknown id {key}')
