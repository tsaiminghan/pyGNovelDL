import os
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT, DEVNULL, CREATE_NO_WINDOW
import tempfile
from shutil import move, copyfile
import html2text
from .settings import GLOBAL, conf_path
from .opencc.wrapper import OpenCC


class HtmlRemove(object):
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, 'inst'):
            cls.inst = cls()
        return cls.inst

    def __init__(self):
        self.obj = html2text.HTML2Text()
        self.obj.ignore_links = True

    def __call__(self, s):
        return self.obj.handle(s)


class STConvert(object):
    @classmethod
    def get_instance(cls):
        if hasattr(cls, 'inst'):
            if not cls.inst.check():
                cls.inst = cls()
        else:
            cls.inst = cls()
        return cls.inst

    def __init__(self):
        self._new(GLOBAL.opencc)

    def check(self):
        return self.conversion == GLOBAL.opencc

    def _new(self, conversion):
        self.conversion = conversion
        if conversion:
            self.obj = OpenCC(conversion)
        else:
            self.obj = None

    def __call__(self, s):
        if self.obj:
            return self.obj.convert(s)
        return s


def _run_cmd(cmd, **kwargs):
    # Handles PyInstaller, don't show console when -w mode
    kwargs['stdout'] = kwargs.get('stdout', PIPE)
    kwargs['stderr'] = kwargs.get('stderr', PIPE)
    kwargs['stdin'] = kwargs.get('stdout', DEVNULL)
    p = Popen(cmd, creationflags=CREATE_NO_WINDOW, **kwargs)

    while p.poll() is None:
        line = p.stdout.readline().strip()
        if line:
            print(line.decode('utf-8'))
    return p.returncode


def aozora_to_epub(book):
    """ workaround: use a tmp to do convert for unicode issues """
    ini = conf_path / 'AozoraEpub3.ini'
    aozora_txt = book.book_file('.aozora.txt')
    epub = book.book_file('.epub')
    tmp = tempfile.mktemp(suffix='.txt')
    jar_path = Path(GLOBAL.AozoraEpub3['path']).parent
    java = GLOBAL.java['path']
    cmd = [java,
           '-Dfile.encoding=UTF-8', '-cp', 'AozoraEpub3.jar',
           'AozoraEpub3', '-enc', 'UTF-8', '-of', '-i', ini]
    if GLOBAL.AozoraEpub3['device']:
        cmd.extend(['-device', GLOBAL.AozoraEpub3['device']])
    if GLOBAL.AozoraEpub3['hor']:
        cmd.append('-hor')
    cmd.append(tmp)

    epub.unlink(missing_ok=True)
    try:
        copyfile(aozora_txt, tmp)
        _run_cmd(cmd, cwd=jar_path, shell=False)
        os.remove(tmp)
        move(tmp[:-4] + '.epub', epub)
    except FileNotFoundError:
        pass
    return epub.exists()


def epub_to_mobi(book):
    epub = book.book_file('.epub')
    mobi = epub.with_suffix('.mobi')
    exe = GLOBAL.kindlegen['path']
    cmd = [exe, epub, GLOBAL.kindlegen['compresslevel']]

    mobi.unlink(missing_ok=True)
    _run_cmd(cmd, shell=False)
    return mobi.exists()


def epub_to_kepub(book):
    # https://pgaskin.net/kepubify/
    epub = book.book_file('.epub')
    kepub = book.book_file('.kepub')
    exe = GLOBAL.kepubify['path']
    cmd = [exe, epub, '-o', kepub]

    kepub.unlink(missing_ok=True)
    _run_cmd(cmd, shell=False)
    return kepub.exists()
