import tkinter as tk
from tkinter import ttk
from functools import partial
from datetime import datetime
import traceback
from pathlib import Path
from ..common import set_enable, is_disabled
from ..common import message_box as messagebox
from ..table import Table
from ..menu import Util, disable_menu
from ...settings import BOOKS, GLOBAL
from ...logger import logger


def create_table(parent):
    return Table(
        parent,
        columns=[{
            'id': 'id',
            'text': '編號',
            'width': 15,
        }, {
            'id': 'author',
            'text': '作者',
            'width': 50,
            'anchor': 'center'
        }, {
            'id': 'book_name',
            'text': '書名',
            'width': 100,
            'anchor': 'center'
        }, {
            'id': 'chapter_number',
            'text': '章節數',
            'width': 50,
            'anchor': 'center'
        }, {
            'id': 'last_update',
            'text': '更新',
            'width': 100,
            'anchor': 'center',
            'sort': 'DESC'
        }], tv_opt={'show': 'headings'}
    )


def bind_menu(tab):
    util = Util(tab.table.tv)
    table = tab.table

    def log(text):
        tab.main.current.put_normal('LOG_MESSAGE', text)

    def create_menu():
        @util.bind_menu('開啟', '網頁')
        def _():
            from ...cmds.browser import Command
            for key in table.selected():
                key = table.set(key, 'id')
                url = BOOKS[key]['toc_url']
                Command.open(url)

        @util.bind_menu('開啟', '資料夾')
        def _():
            from ...cmds.folder import Command
            for key in table.selected():
                key = table.set(key, 'id')
                url = BOOKS[key]['toc_url']
                Command.open(url)

        @util.bind_menu('傳送到', 'kindle')
        def _():
            from ...cmds.send import Command
            if not Command.kindle_exist():
                """ TODO """
                log('找不到kindle裝置')
                return
            for key in table.selected():
                key = table.set(key, 'id')
                url = BOOKS[key]['toc_url']
                log(Command.send(url))

        if GLOBAL.mtp['enable']:
            @util.bind_menu('傳送到', GLOBAL.mtp['device'])
            def _():
                from ...cmds.push import Command
                for key in table.selected():
                    key = table.set(key, 'id')
                    url = BOOKS[key]['toc_url']
                    ret = Command.push(url)
                    if ret == 1:
                        log('檔案複製失敗')
                    elif ret == 2:
                        log(f"找不到{GLOBAL.mtp['device']}")
                    elif ret == 3:
                        log('請開啟手機的MTP')
                    else:
                        log('傳送完成')

        def convert(label):
            @util.bind_menu('轉換格式', label)
            def _():
                from ...cmds.convert import Command
                try:
                    for key in table.selected():
                        key = table.set(key, 'id')
                        url = BOOKS[key]['toc_url']
                        if Command.convert(url, label):
                            log(f'轉換{label}成功')
                        else:
                            log(f'轉換{label}失敗')
                except:
                    logger.exception('轉換%s失敗', label)
                    # traceback.print_exc()
        if formats := GLOBAL.convert:
            for label in formats:
                convert(label)

        @util.bind_menu_set(tab.change_state)
        @util.bind_menu('檢查更新')
        def _():
            for iid in table.selected():
                id = table.set(iid, 'id')
                tab.main.analyzer.put_normal('LIBRARY_UPDATE', [BOOKS[id]])

        @util.bind_menu_set(tab.change_state)
        @util.bind_menu('下載更新')
        def _():
            for iid in table.selected():
                id = table.set(iid, 'id')
                tab.main.worker.put_normal('LIBRARY_DOWNLOAD_UPDATE', [BOOKS[id]])

        @util.bind_menu_set(tab.change_state)
        @util.bind_menu('刪除')
        def _():
            if messagebox('yesno', '注意', '確定刪除？'):
                for iid in table.selected():
                    book_id = table.set(iid, 'id')
                    toc_url = BOOKS[book_id]['toc_url']
                    tab.main.mgr.delete(toc_url)
                BOOKS.sort()
                BOOKS.dump()
                table.remove(*table.selected())
                tab.load_library()
                log('刪除完成')

    util.register(create_menu)


class LibraryTab(ttk.Frame):
    def __init__(self, main_window, master=None, **kw):
        super().__init__(master, **kw)
        self.main = main_window
        self.create_view()

    def create_view(self):
        btn_bar = ttk.Frame(self)
        btn_bar.pack(anchor=tk.W)
        self.btn_update = ttk.Button(btn_bar, text='檢查更新')
        self.btn_update.pack(side=tk.LEFT)
        self.btn_download_update = ttk.Button(btn_bar, text='下載更新')
        self.btn_download_update.pack(side=tk.LEFT)
        self.table = create_table(self)

    def change_state(self, tv, menu, label):
        if is_disabled(self.btn_update):
            disable_menu(menu, label)

    def bind_event(self):
        @self.main.current.register('ANALYSIS_START')
        @self.main.current.register('LIBRARY_DOWNLOAD_UPDATE_START')
        def _():
            set_enable(self.btn_update, False)
            set_enable(self.btn_download_update, False)

        @self.main.current.register('ANALYSIS_FINISH')
        @self.main.current.register('LIBRARY_DOWNLOAD_UPDATE_END')
        def _():
            set_enable(self.btn_update, True)
            set_enable(self.btn_download_update, True)

        def key(item):
            if self.table.sort_on == 'chapter_number':
                return eval(item[0])
            return item[0]

        self.btn_update['command'] = \
            lambda: self.main.analyzer.put_normal('LIBRARY_UPDATE', BOOKS.values())
        self.btn_download_update['command'] = \
            lambda: self.main.worker.put_normal('LIBRARY_DOWNLOAD_UPDATE', BOOKS.values())

        self.load_library()
        self.table.on('sort', partial(Table.on_sort, key=key))
        self.bind_menu()

    def bind_menu(self):
        bind_menu(self)

    @staticmethod
    def item(id, author, book_name, chapter_number, last_update):
        return locals()

    def load_library(self):
        iids = list(self.table.iid_index.keys())
        now = datetime.now()
        for id, v in BOOKS.items():
            is_new = BOOKS.is_new(now, v['last_update'])
            chaps = v['chaps']
            if is_new:
                new_chaps = v['chaps'] - v['chaps_old']
                if new_chaps:
                    chaps = f'{chaps - new_chaps}+{new_chaps}'
            item = self.item(id,
                             v['author'],
                             v['title'],
                             str(chaps),
                             v['last_update'])
            try:
                self.table.update(key=iids.pop(0), **item)
            except IndexError:
                self.table.add(item)
        for iid in iids:
            self.table.remove(iid)
