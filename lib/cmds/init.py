from pathlib import Path
from subprocess import check_output, CalledProcessError
from ._sample import Command as Base
from ..settings import GLOBAL

NAME = 'init'


def setup_opencc():
    opencc_conf = {'1': 's2t',
                   '2': 't2s',
                   '3': 's2tw',
                   '4': 'tw2s',
                   '5': 's2hk',
                   '6': 'hk2s',
                   '7': 's2twp',
                   }
    while True:
        ret = input('''1. s2t,  Simplified Chinese to Traditional Chinese
2. t2s,  Traditional Chinese to Simplified Chinese
3. s2tw, Simplified Chinese to Traditional Chinese (Taiwan Standard)
4. tw2s, Traditional Chinese (Taiwan Standard) to Simplified Chinese
5. s2hk, Simplified Chinese to Traditional Chinese (Hong Kong Standard) 
6. hk2s, Traditional Chinese (Hong Kong Standard) to Simplified Chinese
7. s2twp, s2tw with Taiwanese idiom
8. None, don't use opencc
opencc config, select a number [{}]: '''.format(GLOBAL.opencc))
        if ret in '1234567':
            GLOBAL.opencc = opencc_conf.get(ret)
            break
    print('set opencc to {}'.format(GLOBAL.opencc))


def setup_aozoraepub3():
    path = input('The path of AozoraEpub3: ')
    jar = Path(path).with_name('AozoraEpub3.jar')
    if jar.exists():
        print('find AozoraEpub3, set it')
        GLOBAL.AozoraEpub3['path'] = str(jar.absolute())
    else:
        print('skip to setup AozoraEpub3')

    try:
        GLOBAL.java['path'] = check_output('where java', encoding='utf-8').strip()
    except CalledProcessError:
        print('WARN: AozoraEpub3 need java environment')
        path = input('The path of java: ')
        exe = Path(path).with_name('java.exe')
        if exe.exists():
            print('find java, set it')
            GLOBAL.java['path'] = str(exe.absolute())
        else:
            print('skip to setup java')


def setup_kindlegen():
    path = input('The path of kindlegen: ')
    exe = Path(path).with_name('kindlegen.exe')
    if exe.exists():
        print('find kindlegen, set it')
        GLOBAL.kindlegen['path'] = str(exe.absolute())
    else:
        print('skip to setup kindlegen')


class Command(Base):
    """
Usage: n init <options>
  setup information.
  e.g.
    n init
    n i

  options:
    opencc setup opencc
      e.g.
        n init opencc
        n i opencc"""
    name = NAME

    def __call__(self, *args, **kwargs):
        setup_aozoraepub3()
        setup_kindlegen()
        setup_opencc()
