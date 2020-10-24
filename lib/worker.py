import threading
import queue
import sys
import functools
from .logger import logger

PRI_HIGH = 10
PRI_NORMAL = 20
PRI_LOW = 30


def noop(*_, **__):
    print('NOOP')


class Proxy(object):
    def __init__(self, priority, arg0, args, kwargs):
        self.priority = priority
        self.arg0 = arg0
        self.args = args
        self.kwargs = kwargs

    def __lt__(self, other):
        # for PriorityQueue
        return self.priority < other.priority

    def get(self):
        return self.arg0, self.args, self.kwargs


class Base(object):
    def __init__(self):
        self.que = queue.PriorityQueue()
        self.callback = {'exit': [sys.exit]}

    def run(self):
        try:
            while True:
                message, args, kw = self.que.get(block=True).get()
                callbacks = self.callback.get(message, [noop])
                for callback in callbacks:
                    callback(*args, **kw)
                self.que.task_done()
        except SystemExit:
            pass
        except:
            logger.exception('%s, args=%s kw=%s', message, str(args), str(kw))

    def put_low(self, *args, **kwargs):
        self.put(PRI_LOW, *args, **kwargs)

    def put_high(self, *args, **kwargs):
        self.put(PRI_HIGH, *args, **kwargs)

    def put_normal(self, *args, **kwargs):
        self.put(PRI_NORMAL, *args, **kwargs)

    def put(self, priority, arg0, *args, **kwargs):
        self.que.put(Proxy(priority, arg0, args, kwargs))

    def register(self, message):
        """ this is a decorator with a message parameter """

        def wrapper(function):
            if not self.callback.get(message):
                self.callback[message] = []
            self.callback[message].append(function)
            return function

        return wrapper


class Worker(Base, threading.Thread):

    def __init__(self, *args, **kw):
        Base.__init__(self)
        threading.Thread.__init__(self, *args, **kw)
        self.start()

    def finish(self):
        self.put_high('exit')
        self.join()

    def wait_to_finish(self):
        self.put(float('inf'), 'exit')
        self.join()


class Current(Worker):
    def __init__(self, root, *args, **kw):
        self.root = root
        super().__init__(*args, **kw)

    @staticmethod
    def proxy(callback, kw, *args):
        return callback(*args, **kw)

    def run(self):
        try:
            while True:
                message, args, kw = self.que.get(block=True).get()
                callbacks = self.callback.get(message, [noop])
                for callback in callbacks:
                    if message == 'exit':
                        callback(*args, **kw)
                    else:
                        self.root.after(0, self.proxy, callback, kw, *args)
                self.que.task_done()
        except SystemExit:
            pass
        except:
            logger.exception('%s, args=%s, kw=%s', message, str(args), str(kw))


class Pool(Base):
    @property
    def size(self):
        return len(self.threads)

    def __init__(self, size):
        super().__init__()
        self.callback['thread_exit'] = [self._thread_exit]
        self.threads = []
        self.tid = 0
        self._add_thread(size)

    def _add_thread(self, num):
        for _ in range(num):
            t = threading.Thread(target=self.run, name=f'pool-{self.tid}')
            self.tid += 1
            self.threads.append(t)
            t.start()

    def _thread_exit(self):
        t = threading.current_thread()
        self.threads.remove(t)
        self.que.task_done()
        sys.exit()

    def resize(self, new_size):
        num = new_size - self.size
        if num > 0:
            self._add_thread(num)
        elif num < 0:
            for _ in range(-num):
                self.put(PRI_HIGH, 'thread_exit')
        return self

    def finish(self):
        for _ in self.threads:
            self.put(PRI_HIGH, 'exit')
        for t in self.threads:
            t.join()
        self.threads = []
