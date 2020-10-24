import os
import tkinter as tk
from tkinter import ttk
import traceback
import threading
from pathlib import Path
from .common import set_text
from .tabs.mission import MissionTab
from .tabs.domain import DomainTab
from .tabs.settings import SettingsTab
from .tabs.addurl import AddTab
from .tabs.library import LibraryTab
from ..settings import GLOBAL
from ..logger import logger
from ..worker import Current, Worker, Pool
from ..mission_manager import MissionMgr
from ..systray.wrapper import SysTrayIcon
from ..util import pid_exists


class ViewMix(object):
    tab_id = {
        'mission': 0,
        'add': 1,
        'lib': 2,
        'domain': 3,
        'settings': 4,
    }

    def create_view(self):
        root = tk.Tk()
        root.title('pyGNovelDL')

        self.create_btn_bar(root)

        # notebook
        notebook = ttk.Notebook(root)
        notebook.pack(expand=True, fill=tk.BOTH)

        # mission
        tab = MissionTab(self, notebook)
        self.mission_tab = tab
        notebook.add(tab, text='任務')

        # addurl
        tab = AddTab(self, notebook)
        self.add_tab = tab
        notebook.add(tab, text='加入連結')

        # library
        tab = LibraryTab(self, notebook)
        self.lib_tab = tab
        notebook.add(tab, text='圖書館')

        # domain
        tab = DomainTab(self, notebook)
        self.domain_tab = tab
        notebook.add(tab, text='支援的網域')

        # settings
        tab = SettingsTab(self, notebook)
        self.settings_tab = tab
        notebook.add(tab, text='設定')

        # status bar
        statusbar = ttk.Label(root, text='', anchor=tk.W)
        statusbar.pack(anchor=tk.W)
        self.statusbar = statusbar

        self.notebook = notebook
        self.root = root

    def create_btn_bar(self, root):
        """Draw the button bar"""
        buttonbox = ttk.Frame(root)
        buttonbox.pack(anchor=tk.NW)

        btnaddurl = ttk.Button(buttonbox, text='加入連結')
        btnaddurl.pack(side=tk.LEFT)
        self.btn_addurl = btnaddurl

        btnstartstop = ttk.Button(buttonbox, text='開始下載')
        btnstartstop.pack(side=tk.LEFT)
        self.btn_start_stop = btnstartstop


class EventMix(object):
    def bind_btn(self):
        def addurl():
            widget = self.add_tab.text
            self.notebook.select(self.tab_id['add'])
            widget.focus_set()

        self.btn_addurl['command'] = addurl
        self.btn_start_stop['command'] = lambda: self.current.put_normal('DOWNLOAD_START')

    def bind_systray(self):
        def on_quit(systray):
            self.root.wm_deiconify()

        def visible(event):
            if self.systray:
                self.systray.shutdown()
                self.systray = None

        def invisible(event):
            self.root.wm_withdraw()
            systray = SysTrayIcon(None, 'pyGNovelDL', on_quit=on_quit)
            systray.start()
            self.systray = systray
        self.systray = None
        self.btn_addurl.bind('<Map>', visible)
        self.btn_addurl.bind('<Unmap>', invisible)

    def bind_event(self):
        self.mission_tab.bind_event()
        self.domain_tab.bind_event()
        self.add_tab.bind_event()
        self.lib_tab.bind_event()
        self.bind_btn()
        self.bind_systray()


class MainWindow(ViewMix, EventMix):
    def __init__(self):
        filelock = Path('.~lock')
        if filelock.exists():
            pid = int(filelock.read_text())
            if pid_exists(pid):
                return
        else:
            filelock.write_text(str(os.getpid()))

        self.filelock = filelock
        logger.init()
        threading.current_thread().setName('main')
        self.create_view()
        self.analyzer = Worker(name='analyzer')
        self.worker = Worker(name='worker')
        self.pool = Pool(0)
        self.current = Current(self.root)
        self.mgr = MissionMgr(self)
        self.register()
        self.bind_event()
        self.root.protocol('WM_DELETE_WINDOW', self.close_window)
        self.worker.put_normal('RESTORE_MISSIONS')
        self.root.mainloop()

    def close_window(self):
        self.mgr.running = 9999
        self.filelock.unlink()

        def close():
            self.current.finish()
            self.pool.finish()
            self.analyzer.finish()
            self.worker.finish()
            self.root.after(1, self.root.destroy)
            self.mgr.save()
        threading.Thread(target=close).start()

    def register(self):
        self.mgr.register()

        @self.pool.register('DOWNLOAD')
        def _(mission, tree_key):
            state = 'FAIL'
            try:
                key = mission.get_key(tree_key)
                self.mgr.update_state(mission, mission, state='DOWNLOAD')
                self.mgr.update_state(mission, tree_key, state='DOWNLOAD')
                if mission.dl_chapter(key):
                    state = 'OK'
            except:
                logger.exception('dl_chapter error')
                # traceback.print_exc()

            self.mgr.update_state(mission, tree_key, state=state)

            convert_fail = False
            if mission.is_dl_finished:
                mission.book_dump()
                if mission.is_ok:
                    self.current.put_normal('UPDATE_PARENT', mission, state='CONVERT')
                    for fmt in GLOBAL.convert:
                        if not mission.convert(fmt):
                            self.current.put_normal('LOG_MESSAGE',
                                                    f'{mission.book.name}轉換{fmt}失敗')
                            convert_fail = True
                            break

            if convert_fail:
                self.current.put_normal('UPDATE_PARENT', mission, state='CONVERT_FAIL')
            else:
                if GLOBAL.pygnoveldl['clean_finished'] and mission.is_ok:
                    self.current.put_normal('MISSION_REMOVE', mission)
                else:
                    self.current.put_normal('UPDATE_PARENT', mission)
            with self.mgr.running_lock:
                self.mgr.net_usage_remove_lock(mission)
                self.mgr.running -= 1
                self.current.put_normal('START')

        @self.current.register('DOWNLOAD_START')
        def _():
            self.btn_start_stop.config(text='停止下載')
            self.btn_start_stop['command'] = lambda: self.current.put_normal('DOWNLOAD_STOP')
            self.pool.resize(GLOBAL.pool['size'])
            with self.mgr.running_lock:
                self.mgr.running = 0

        @self.current.register('DOWNLOAD_STOP')
        def _():
            self.btn_start_stop.config(text='開始下載')
            self.btn_start_stop['command'] = lambda: self.current.put_normal('DOWNLOAD_START')
            with self.mgr.running_lock:
                self.mgr.running = 9999

        @self.current.register('START')
        @self.current.register('DOWNLOAD_START')
        def _():
            size = GLOBAL.pool['size']
            for _ in range(size):
                with self.mgr.running_lock:
                    if size > self.mgr.running:
                        mission, tree_key = self.mgr.get_download_item_lock()
                        if mission:
                            self.mgr.running += 1
                            self.pool.put_normal('DOWNLOAD', mission, tree_key)
            if self.mgr.running == 0:
                self.current.put_normal('DOWNLOAD_STOP')

        @self.current.register('LOG_MESSAGE')
        def _(text):
            set_text(self.statusbar, text)

        @self.current.register('LIBRARY_RELOAD')
        def _():
            self.lib_tab.load_library()

        @self.worker.register('LIBRARY_DOWNLOAD_UPDATE')
        def _(books):
            self.current.put_normal('LIBRARY_DOWNLOAD_UPDATE_START')
            add = 0
            for book in books:
                url = book['toc_url']
                mission = self.mgr.get_lock(url)
                if keys := list(mission.get_new_chapter_keys()):
                    add += 1
                    self.current.put_normal('MISSION_ADD', mission, keys)
            self.current.put_normal('LOG_MESSAGE', f'更新數: {add}')
            self.current.put_normal('LIBRARY_DOWNLOAD_UPDATE_END')

        @self.analyzer.register('ANALYSIS')
        def _(url):
            self.current.put_normal('ANALYSIS_START')
            try:
                mission = self.mgr.get_lock(url)
                if mission.analysis():
                    self.current.put_normal('LOG_MESSAGE', f'分析完成: {mission.book.name}')
                    self.current.put_normal('MISSION_ADD', mission, list(mission.chapters.keys()))
                    self.current.put_normal('LIBRARY_RELOAD')
                else:
                    self.mgr.put_lock(mission.toc_url)
                    self.current.put_normal('LOG_MESSAGE', f'分析失敗: {mission.toc_url}')
            except ModuleNotFoundError:
                self.current.put_normal('LOG_MESSAGE', '不支援此網址')
            except Exception as e:
                # traceback.print_exc()
                logger.exception('analysis error')
                self.current.put_normal('LOG_MESSAGE', str(e))
            self.current.put_normal('ANALYSIS_FINISH')

        @self.analyzer.register('LIBRARY_UPDATE')
        def _(books):
            """ TODO: this will block  """
            self.current.put_normal('ANALYSIS_START')
            fail = 0
            new = 0
            try:
                symbol = ['--', '＼', '｜', '／']
                for idx, book in enumerate(books):
                    toc_url = book['toc_url']
                    mission = self.mgr.get_lock(toc_url)
                    self.current.put_normal('LOG_MESSAGE', '檢查更新 ' + symbol[idx % 4])
                    chapters = len(mission.chapters)
                    if mission.analysis():
                        if len(mission.chapters) > chapters:
                            new += 1
                            self.current.put_normal('LIBRARY_RELOAD')
                    else:
                        self.mgr.put_lock(toc_url)
                        fail += 1
                        self.current.put_normal('LOG_MESSAGE', f'分析失敗: {mission.name}')

            except Exception as e:
                fail += 1
                logger.exception('analysis error')
                # traceback.print_exc()
                self.current.put_normal('LOG_MESSAGE', str(e))
            self.current.put_normal('LOG_MESSAGE', f'檢查更新完成, 更新:{new} 失敗:{fail}')
            self.current.put_normal('ANALYSIS_FINISH')
