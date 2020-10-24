from ._sample import Command as Base

NAME = 'support'


class Command(Base):
    """
Usage: n support
  list support information"""
    name = NAME

    def __call__(self, cmd='help', *args, **kwargs):
        from ..websites import _mod
        print(f'Support {len(_mod.mod_list)} websites:')
        for mod in _mod.mod_list:
            print(f'  {mod.NETLOC}')

        from . import cmd_list
        print('\nSupport commands:')
        for cmd in cmd_list:
            print(f'  {cmd}')
