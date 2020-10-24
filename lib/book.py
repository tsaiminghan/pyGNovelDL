from .settings import Book as Database
from .settings import YamlBase, BOOKS
from .websites import get_mod
from .settings import data_path
from .aozora import Aozora
from .convert import aozora_to_epub, epub_to_mobi, epub_to_kepub


def safe_path(path):
    r""" window: not allow symbol \/:*?"<>|
    """
    symbols = {'\\': '＼',
               '/': '／',
               ':': '：',
               '*': '＊',
               '?': '？',
               '"': '”',
               '<': '＜',
               '>': '＞',
               '|': '｜', }
    ret = ''
    for c in path:
        ret += symbols.get(c, c)
    return ret


class Content(YamlBase):
    @staticmethod
    def item(title, chapter, text):
        return locals()


class Book(Database):
    """
    functions about path, convert
    """

    def __init__(self, url, load=True):
        self.mod = get_mod(url)
        self.mod.set(self)

        if load:
            if d := BOOKS.find(toc_url=self.mod.toc_url)[1]:
                self.reinit(d['author'],
                            d['title'])

    @property
    def name(self):
        return f'[{self.author}] {self.title}'

    def reinit(self, author, title):
        self.author = author
        self.title = title
        filename = data_path / self.mod.netloc / self.name / 'database.yaml'
        self.init(filename)
        self.toc_url = self.mod.toc_url
        self.chap_url = self.mod.chap_url

    def analysis(self, **option):
        ok, result = self.mod.analysis(**option)
        if ok:
            self.reinit(self.mod.author, self.mod.title)
            self.raw_path.mkdir(parents=True, exist_ok=True)
            self.content_path.mkdir(parents=True, exist_ok=True)
            self.update_to(result)
            self.update_from(result)

            item = BOOKS.item(title=self.title,
                              author=self.author,
                              chaps=len(self.chapters),
                              timestamp=self.mod.timestamp,
                              toc_url=self.toc_url)
            BOOKS.update(item)
            self.dump()

        return ok

    def dl_chapter(self, key, **option):
        return self.mod.dl_chapter(key, **option)

    def book_file(self, suffix):
        return self.book_path / f'{self.name}{suffix}'

    @property
    def book_path(self):
        return self.filename.parent

    @property
    def raw_path(self):
        return self.book_path / 'raw'

    @property
    def content_path(self):
        return self.book_path / 'content'

    def content_file(self, name):
        p = self.content_path / safe_path(name)
        return p.with_suffix('.yaml')

    def raw_file(self, name):
        return self.raw_path / safe_path(name)

    def write_raw(self, name, text):
        p = self.raw_file(name)
        p.write_text(text, encoding='utf-8')

    def write_content(self, key, text):
        d = self.chapters.get(key)
        c = Content(self.content_file(key))
        c.data = c.item(title=d['title'],
                        chapter=d['chapter'],
                        text=text)
        c.dump()

    def iter_contents(self):
        for key in self.chapters:
            yield self.content_file(key)

    def aozora(self):
        """ content to aozora """
        filename = self.book_path / f'{self.name}.aozora.txt'
        with Aozora(filename) as aoz:
            aoz.bookinfo(url=self.toc_url,
                         author=self.author,
                         bookname=self.title)

            for y in map(YamlBase, self.iter_contents()):
                if not y.load():
                    return False
                if y.chapter:
                    aoz.chapter(y.chapter)
                aoz.title(y.title)
                for line in y.text.splitlines():
                    aoz.paragraph(line)
                aoz.change_page()
            return True

    def txt(self):
        """ content to text"""
        filename = self.book_path / f'{self.name}.txt'
        with filename.open('w', encoding='utf-8') as f:
            for y in map(YamlBase, self.iter_contents()):
                if not y.load():
                    return False
                f.write(y.title + '\n' * 2)
                f.write(y.text + '\n' * 2)
            return True

    def epub(self):
        return aozora_to_epub(self)

    def mobi(self):
        return epub_to_mobi(self)

    def kepub(self):
        return epub_to_kepub(self)
