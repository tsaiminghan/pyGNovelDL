import sys
from ._sample import Command as Base

NAME = 'help'


class Command(Base):
    """
Usage: n <command> [arguments...]

  command:
    browser   open the book url.
    convert   convert books to different format
    download  download books.
    folder    open the book folders
    help      use 'n help <command>' to get command details.
    init      initial setup
    list      list information of books
    push      copy books to MTP device by id
    remove    remove download files by id
    support   list support website and commands
    send      copy books to Kindle device by id
    update    update books by id

    each command could use head words of a command to instead of full one.
    e.g. n download <url> -> n d <url>
         n list           -> n l
         n support        -> n su"""
    name = NAME

    @staticmethod
    def match(cmd):
        from . import cmd_list
        cmds = [c for c in cmd_list if c.startswith(cmd)]
        if len(cmds) == 1:
            return cmds[0]
        print('WARN: "{}" matches {} command(s): {}'
              .format(cmd, len(cmds), cmds))
        sys.exit(-1)

    def __call__(self, cmd='help', *args, **kwargs):
        from . import get_cmd
        cmd = self.match(cmd)
        cmd = get_cmd(cmd)
        print(cmd.__doc__)
