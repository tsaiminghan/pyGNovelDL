import threading
from .book import Book
from .settings import BOOKS, GLOBAL
from .download import proxies
from .download import State as DLState
from .util import split
from .logger import logger


class State(object):
    INIT = '初始化'
    ANALYSIS = '分析中'
    DOWNLOAD = '下載中'
    CONVERT = '轉換中'
    CONVERT_FAIL = '轉換失敗'
    DELETE = '刪除中'
    READY = '等待中'
    OK = '下載完成'
    FAIL = '下載失敗'
    FINISHED = '任務完成'
    usage = {}

    def __init__(self):
        self.lock = threading.Lock()
        self.iid = 0

    def __getitem__(self, key):
        if key == 'ALL':
            return self.all
        return self.usage[key]

    @classmethod
    def get_text(cls, state):
        return getattr(cls, state)

    def new(self):
        self.all = {}
        self.usage = dict(INIT=[],
                          ANALYSIS=[],
                          DOWNLOAD=[],
                          CONVERT=[],
                          DELETE=[],
                          READY=[],
                          OK=[],
                          FAIL=[],
                          FINISHED=[])

    @property
    def is_empty(self):
        return len(self.all) == 0

    def _remove(self, tree_key):
        _, old_state = self.all[tree_key]
        del self.all[tree_key]
        self.usage[old_state].remove(tree_key)

    def remove_lock(self, tree_key):
        with self.lock:
            self._remove(tree_key)

    def set_lock(self, *args, **kw):
        """   OK=tree_key """
        with self.lock:
            if args:
                iter = split(args, 2)
            else:
                iter = kw.items()

            for state, tree_key in iter:
                exist = tree_key in self.all
                if exist:
                    iid, old_state = self.all[tree_key]
                    if old_state == state:
                        continue
                    self.usage[old_state].remove(tree_key)
                else:
                    self.iid += 1
                    iid = self.iid

                self.all[tree_key] = (iid, state)
                self.usage[state].append(tree_key)
                if exist:
                    sorted(self.usage[state], key=lambda x: x[0])


class Mission(object):

    def __init__(self, url, load=False):
        self.book = Book(url, load=load)
        self.lock = threading.Lock()
        self.mid = -1
        self.dirty = False
        self.is_delete = False
        self.usage = State()
        self.usage.new()

    def todict(self):
        keys = []
        for tree_key, (iid, state) in self.usage['ALL'].items():
            if state != 'OK':
                keys.append(self.get_key(tree_key))
        return dict(
            toc_url=self.toc_url,
            keys=keys
        )

    @staticmethod
    def proxy():
        option = {}
        if GLOBAL.proxy['enable']:
            option['proxies'] = proxies(**GLOBAL.proxy)
        return option

    @property
    def toc_url(self):
        return self.book.toc_url

    def load(self):
        if d := BOOKS.find(toc_url=self.book.mod.toc_url)[1]:
            self.book.reinit(d['author'],
                             d['title'])

    def set_mid(self, mid):
        self.mid = mid

    def book_dump(self):
        with self.lock:
            if self.is_delete:
                return
            if self.dirty:
                self.book.dump()
                self.dirty = False

    def analysis(self):
        self.dirty = False
        with self.lock:
            if self.is_delete:
                return False
            return self.book.analysis(**self.proxy())

    def convert(self, fmt):
        with self.lock:
            if self.is_delete:
                return False
            return getattr(self.book, fmt)()

    def delete(self):
        from .cmds.remove import Command
        with self.lock:
            self.is_delete = True
            Command.remove(toc_url=self.toc_url)

    def dl_chapter(self, key):
        with self.lock:
            if self.is_delete:
                return False
            if ok := self.book.dl_chapter(key, **self.proxy()):
                self.dirty = True
            return ok

    def parent_item(self):
        """ TODO: timestamp get atfter analysis"""
        if d := BOOKS.find(toc_url=self.toc_url)[1]:
            timestamp = d['timestamp'].split()[0]
        else:
            timestamp = self.book.mod.timestamp.split()[0]

        return {'name': f'{self.book.name} (0/0)',
                'host': self.book.mod.name,
                'state': State.INIT,
                'last_update': timestamp,
                }

    def child_item(self, key):
        """ TODO: key maybe not exists """
        d = self.book.chapters[key]
        return {'name': d['title'],
                'state': State.INIT,
                }

    def get_new_chapter_keys(self):
        if self.chapters:
            for k, v in list(self.chapters.items()):
                if v['state'] != DLState.CONTENT_EXIST:
                    yield k

    @property
    def is_dl_finished(self):
        total = len(self.usage['ALL'])
        ok = len(self.usage['OK'])
        fail = len(self.usage['FAIL'])
        return total == ok + fail

    @property
    def is_ok(self):
        total = len(self.usage['ALL'])
        ok = len(self.usage['OK'])
        return total == ok and not self.is_delete

    @property
    def chapters(self):
        return self.book.chapters

    @property
    def name(self):
        return self.book.name

    def to_key(self, key):
        return f'{self.mid}_{key}'

    @staticmethod
    def get_key(key):
        return key.partition('_')[2]
