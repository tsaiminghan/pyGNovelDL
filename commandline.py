from lib.command import Command
import sys
import getopt

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], 'g', ['gui'])
    for o, a in opts:
        if o in ('-g', '--gui'):
            from lib.gui.main_window import MainWindow
            MainWindow()
            sys.exit()
    argv = []
    kw = {}
    for a in args:
        if '=' in a:
            k, v = a.split('=')
            kw[k] = v
        else:
            argv.append(a)

    Command(*argv, **kw)()
