from pathlib import Path
from . import browser
from . import convert
from . import download
from . import folder
from . import help
from . import init
from . import list
from . import push
from . import remove
from . import send
from . import support
from . import update
from ..modloader import ModLoader


class Loader(ModLoader):
    def __init__(self):
        self.mod_list = [
            browser,
            convert,
            download,
            folder,
            help,
            init,
            list,
            push,
            remove,
            send,
            support,
            update,
        ]

    @property
    def support(self):
        return [mod.NAME for mod in self.mod_list]

    @staticmethod
    def compare(mod, value):
        return mod.NAME == value

    def get_mods(self, cmd, default=None):
        return super().get_mods(cmd, default).Command()


_mod = Loader()
get_cmd = _mod.get_mods
cmd_list = _mod.support
