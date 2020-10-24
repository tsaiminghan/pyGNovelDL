from datetime import datetime
from ._sample import Command as Base
from ._color_console import MAGENTA
from ..settings import BOOKS

NAME = 'list'


class Command(Base):
    """
Usage: n list [<id>]
  show the list id of all novels.
    DATE: the last time to check (update_time)

  e.g.
    n list
    n l

  show information for a special id of novels.
    last_update:  the last time to check
    update_time:  the time of newest chapter
    chaps:        number of chapters
    dir:          download folder

  e.g.
    n l 0  """
    name = NAME

    @staticmethod
    def print_list():
        color = MAGENTA()
        print('{0:^4} | {1:^10} | {2:>5} | {3}'.format(
            'ID', 'DATE', 'CHAPS', 'TITLE'))
        now = datetime.now()
        for idx, v in BOOKS.items():

            is_new = BOOKS.is_new(now, v['last_update'])

            print('{0:>4} | {1:^10} | {2:>5} | {3}'.format(
                idx,
                v['timestamp'].split()[0],
                v['chaps'],
                v['title']), end='')

            color.start(is_new)
            if is_new:
                new_chaps = v['chaps'] - v['chaps_old']
                print('*new({})'.format(new_chaps) if new_chaps > 0 else '*new')
            else:
                print('')
            color.end()

    @staticmethod
    def print(d):
        for k in sorted(d.keys()):
            print(f' {k:11} | {d[k]}')

    @classmethod
    def _print(cls, key):
        if d := BOOKS.get(key):
            cls.print(d)
        else:
            print(f'unknown id {key}')

    def __call__(self, *args, **kwargs):
        if args:
            for key in args:
                self._print(key)
        else:
            self.print_list()
