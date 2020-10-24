import sys
from .cmds import get_cmd, cmd_list


class Command(object):
    _commands = cmd_list
    cmd = 'help'

    @classmethod
    def match(cls, cmd):
        cmds = [c for c in cls._commands if c.startswith(cmd)]
        if len(cmds) == 1:
            return cmds[0]
        else:
            print('WARN: "{}" matches {} command(s): {}'
                  .format(cmd, len(cmds), cmds))
            sys.exit(-1)

    def __init__(self, *args, **kwargs):
        self.args = args[1:]
        self.kwargs = kwargs
        if len(args) > 0:
            cmd = args[0]
            self.cmd = self.match(cmd)

    def __call__(self):
        if self.cmd:
            command = get_cmd(self.cmd)
            return command(*self.args, **self.kwargs)
