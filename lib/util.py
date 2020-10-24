import threading
import time
import functools
import os


def split(s, length):
    while s:
        yield s[:length]
        s = s[length:]


class Sync(object):
    def __init__(self):
        self._lock = threading.Lock()

    def __call__(self, function):
        def wrapper(*args, **kwargs):
            with self._lock:
                ret = function(*args, **kwargs)
            return ret

        return wrapper


def timelog(arg0, name=None):
    if not callable(arg0):
        return functools.partial(timelog, name=arg0)

    if name is None:
        name = arg0.__name__

    def wrapper(*args, **kwargs):
        st = time.time()
        try:
            print(f'[{name}] ----------> Start')
            return arg0(*args, **kwargs)
        finally:
            print('[{}] ----------> End in {}'.format(
                name, time.time() - st))

    wrapper.__name__ = name
    return wrapper


if os.name == 'posix':
    def pid_exists(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True
else:
    def pid_exists(pid):
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x100000
        process = kernel32.OpenProcess(SYNCHRONIZE, 0, pid)
        if process != 0:
            kernel32.CloseHandle(process)
            return True
        else:
            return False

