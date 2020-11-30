import atexit
import yaml
from pathlib import Path
import copy
import sys
from datetime import datetime, timedelta


def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return Path(sys.executable).parent
    return Path(__file__).parents[1]


_tfmt = '%Y-%m-%d %H:%M'
_root = app_path()
conf_path = _root / 'config'
data_path = _root / 'data'


class YamlBase(object):
    data = {}

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        return self.loads()

    def loads(self, filename=None):
        if filename:
            self.filename = filename

        try:
            with self.filename.open(encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
        except FileNotFoundError:
            pass
        return self.data

    def dump(self, **kwargs):
        return self.dumps(data=None, **kwargs)

    def dumps(self, data=None, **kwargs):
        if not data:
            data = self.data
        with self.filename.open('w', encoding='utf-8') as f:
            kwargs['sort_keys'] = kwargs.get('sort_keys', False)
            kwargs['default_flow_style'] = kwargs.get('default_flow_style', False)
            kwargs['allow_unicode'] = kwargs.get('allow_unicode', True)
            yaml.dump(data, f, **kwargs)

    def __getattr__(self, key):
        return self.data.get(key, None)

    def __setattr__(self, key, value):
        if key in self.data:
            self.data[key] = value
        else:
            super().__setattr__(key, value)


class Global(YamlBase):
    filename = conf_path / 'global.yaml'

    def __init__(self, sort_keys=True):
        self.filename.parent.mkdir(exist_ok=True)
        self.load()
        atexit.register(lambda: self.dump(sort_keys=sort_keys))


class Books(Global):
    """
    { id: {
            author:
            title:
            timestamp:
            chaps:
            chaps_old:
            last_check:
            last_update:
            toc_url:
        },
    }
    """
    filename = conf_path / 'books.yaml'

    def __init__(self):
        super().__init__(sort_keys=False)

    def items(self):
        for r in self.data.items():
            yield r

    def keys(self):
        for r in self.data.keys():
            yield r

    def values(self):
        for r in self.data.values():
            yield r

    def __getitem__(self, key):
        return self.data[str(key)]

    def __len__(self):
        return len(self.data)

    def get(self, key, default=None):
        return self.data.get(str(key), default)

    @staticmethod
    def is_new(now, past, hours=6):
        past = datetime.strptime(past, _tfmt)
        return (now - past) <= timedelta(hours=hours)

    @staticmethod
    def item(author='', chaps=0, chaps_old=0, last_check='',
             last_update='', timestamp='',  title='', toc_url=''):
        last_check = datetime.strftime(datetime.now(), _tfmt)
        return locals()

    def find(self, **kwargs):
        if 'toc_url' in kwargs:
            for key, item in self.data.items():
                if kwargs['toc_url'] == item['toc_url']:
                    return key, item
        if 'id' in kwargs:
            key = kwargs['id']
            return key, self.data.get(key)
        return None, None

    def remove(self, **kwargs):
        key = self.find(**kwargs)[0]
        if key:
            del self.data[key]

    def sort(self):
        d = {}
        for idx, key in enumerate(self.data.keys()):
            d[str(idx)] = self.data[key]
        self.data = d

    def update(self, item):
        old_item = self.find(toc_url=item['toc_url'])[1]
        if old_item:
            item['chaps_old'] = old_item['chaps_old']
            item['last_update'] = old_item['last_update']
            if old_item['chaps'] != item['chaps']:
                item['last_update'] = item['last_check']
                now = datetime.now()
                if not self.is_new(now, old_item['last_update']):
                    old_item['chaps_old'] = old_item['chaps']
            old_item.update(item)
        else:
            item['chaps_old'] = item['chaps']
            item['last_update'] = item['last_check']
            self.data[str(len(self))] = item
        self.dump()


class Book(YamlBase):
    """
    functions about data control

    yaml format:
    {
        toc_url: string
        chap_url: string
        chapters: {
            herf0: {
                title: string
                href: []
                chapter: string
                state: number
            },
        }
    }
    """

    @staticmethod
    def item(toc_url='', chap_url='', chapters={}):
        return {'toc_url': toc_url,
                'chap_url': chap_url,
                'chapters': chapters.copy()}

    def __init__(self, filename=None):
        self.init(filename)

    def init(self, filename):
        self.data = self.item()
        self.filename = filename
        self.load()

    def iter_chapters(self):
        if self.chapters:
            for c in self.chapters.values():
                yield c

    def _append(self, chapters):
        """ append chap_url """
        chap_url = self.chap_url
        for c in chapters:
            c['href'] = [chap_url + h for h in c['href']]

    def _remove(self, chapters):
        """ remove chap_url """
        length = len(self.chap_url)
        for c in chapters:
            c['href'] = [h[length:] for h in c['href']]

    def load(self):
        super().load()
        self._append(self.iter_chapters())

    def dump(self):
        chapters = copy.deepcopy(self.chapters)
        self._remove(chapters.values())
        data = self.item(chapters=chapters,
                         toc_url=self.toc_url,
                         chap_url=self.chap_url)
        super().dumps(data)

    def update_from(self, new_dict):
        """ from new_list to data """
        self.chapters = new_dict.copy()

    def update_to(self, new_dict):
        """ from data to new_list """
        old_dict = self.chapters
        for key, value in new_dict.items():
            new_dict[key] = old_dict.get(key, value)
        return new_dict


GLOBAL = Global()
BOOKS = Books()

if __name__ == '__main__':
    print('global=', GLOBAL.data)
    print('books=', BOOKS.data)
