from importlib import import_module


def _import_mod_file(prefix, file):
    return import_module(f'{prefix}.{file.name[:-3]}')


class ModLoader(object):
    def __init__(self, prefix, path):
        self.mod_list = []
        self.load(prefix, path)

    def load(self, prefix, path):
        for f in path.glob('*.py'):
            if not f.name.startswith('_'):
                self.mod_list.append(_import_mod_file(prefix, f))

    @staticmethod
    def compare(mod, value):
        raise NotImplementedError

    def get_mod(self, value):
        return self.get_mods(value)

    def get_mods(self, value, default=None):
        for mod in self.mod_list:
            if self.compare(mod, value):
                return mod
        if default:
            return default
        raise ModuleNotFoundError(f'No module for {value}')
