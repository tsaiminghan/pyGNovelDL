import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
from lib.gui.common import set_text
from lib.settings import GLOBAL


class Base(object):
    def __init__(self, main_window, root):
        self.main = main_window
        self.root = root
        self.init = False

    @staticmethod
    def register(widget, callback, *args):
        vcmd = (widget.register(callback), *args)
        widget.config(validate='key', validatecommand=vcmd)

    def log(self, text):
        self.main.current.put_normal('LOG_MESSAGE', text)

    def create_view(self):
        self.init = True

    def to_dict(self):
        raise NotImplemented


class Environment(Base):
    formats = ['txt', 'aozora', 'epub', 'mobi', 'kepub']

    @staticmethod
    def file_dialog(curdir, filetype):
        return filedialog.askopenfilename(initialdir=curdir,
                                          title="Select file",
                                          filetypes=(filetype, ("all files", "*.*")))

    def create_view(self):
        super().create_view()

        def create_path_item(root, key):
            path = f'{key}_path'
            btn = f'{key}_btn'
            frame = ttk.Frame(root)
            frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
            tk.Label(frame, text='路徑:').pack(side=tk.LEFT)
            setattr(self, path, tk.Entry(frame))
            getattr(self, path).pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, btn, tk.Button(frame, text='...'))
            getattr(self, btn).pack(side=tk.LEFT)
            getattr(self, btn).bind("<ButtonRelease-1>", self.btn_callback)

        def create_radiobutton_item(root, label, var,
                                    texts, values, callback):
            frame = ttk.Frame(root)
            frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
            tk.Label(frame, text=label).pack(side=tk.LEFT)
            for text, value in zip(texts, values):
                ttk.Radiobutton(frame, text=text, variable=var,
                                value=value, command=callback).pack(side=tk.LEFT)

        frame0 = ttk.Frame(self.root)
        frame0.pack(anchor=tk.NW, fill=tk.X)
        lf = tk.LabelFrame(frame0, text='Java')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_path_item(lf, 'java')

        lf = tk.LabelFrame(frame0, text='AozoraEpub3 (aozora -> epub)')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_path_item(lf, 'AozoraEpub3')
        self.hor = tk.BooleanVar(value=GLOBAL.AozoraEpub3['hor'])
        create_radiobutton_item(lf, '排版:', self.hor,
                                ('直排', '橫排'),
                                (False, True), self.hor_callback)

        lf = tk.LabelFrame(frame0, text='kindlegen (epub -> mobi)')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_path_item(lf, 'kindlegen')
        self.compresslevel = tk.StringVar(value=GLOBAL.kindlegen['compresslevel'])
        create_radiobutton_item(lf, '壓縮:', self.compresslevel,
                                ('不壓縮', '標準DOC壓縮', 'Kindle Huffdic壓縮'),
                                ('-c0', '-c1', '-c2'), self.compress_callback)

        lf = tk.LabelFrame(frame0, text='kepubify (epub -> kepub)')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_path_item(lf, 'kepubify')

        lf = tk.LabelFrame(frame0, text='電子書格式 (下載後自動轉換)')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        for text in self.formats:
            cb = self.create_cbox(lf, text=text)
            cb.pack(side=tk.LEFT)
            setattr(self, text, cb)
            cb.bind("<ButtonRelease-1>", self.ebook_callback)

        self.set_default()

    @staticmethod
    def create_cbox(root, **kw):
        cb = ttk.Checkbutton(root, **kw)
        cb.state(('!alternate',))
        return cb

    def btn_callback(self, event):
        def do(btn, key, filetype):
            entry = getattr(self, f'{key}_path')
            button = getattr(self, f'{key}_btn')
            if btn == button:
                p = Path(entry.get())
                if filename := self.file_dialog(p.parent, filetype):
                    filename = str(Path(filename))
                    set_text(entry, filename)
                    getattr(GLOBAL, key)['path'] = filename
                return True
            return False

        btn = event.widget
        do(btn, 'java', ('java.exe', 'java.exe')) or \
        do(btn, 'AozoraEpub3', ('AozoraEpub3.jar', 'AozoraEpub3.jar')) or \
        do(btn, 'kepubify', ('kepubify', 'kepubify*.exe')) or \
        do(btn, 'kindlegen', ('kindlegen.exe', 'kindlegen.exe'))

    def hor_callback(self):
        GLOBAL.AozoraEpub3['hor'] = self.hor.get()

    def compress_callback(self):
        GLOBAL.kindlegen['compresslevel'] = self.compresslevel.get()

    def ebook_callback(self, event):
        cbox = event.widget
        lst = []
        text = cbox['text']
        enable = cbox.instate(('!selected',))
        if text in ['mobi', 'kepub']:
            if enable:
                self.epub.state(('selected',))
                self.aozora.state(('selected',))
        elif text == 'epub':
            if enable:
                self.aozora.state(('selected',))
            else:
                self.kepub.state(('!selected',))
                self.mobi.state(('!selected',))
        elif text == 'aozora':
            if not enable:
                self.epub.state(('!selected',))
                self.kepub.state(('!selected',))
                self.mobi.state(('!selected',))

        for text in self.formats:
            cb = getattr(self, text)
            if cbox == cb:
                if cb.instate(('!selected',)):
                    lst.append(text)
            elif cb.instate(('selected',)):
                lst.append(text)
        GLOBAL.convert = lst

    def set_default(self):
        for ebook in GLOBAL.convert:
            getattr(self, ebook).state(('selected',))
        for key in ['java', 'AozoraEpub3', 'kepubify', 'kindlegen']:
            set_text(getattr(self, f'{key}_path'), getattr(GLOBAL, key)['path'])


class Network(Base):
    keys = ['identity', 'host', 'port', 'password']

    def create_view(self):
        super().create_view()

        def create_item(root, texts, keys):
            frame = ttk.Frame(root)
            frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
            for text, key in zip(texts, keys):
                tk.Label(frame, text=text).pack(side=tk.LEFT)
                setattr(self, key, tk.Entry(frame))
                getattr(self, key).pack(side=tk.LEFT)
                set_text(getattr(self, key), GLOBAL.proxy[key])
                self.register(getattr(self, key), self.entry_callback, '%P', '%W')

        frame0 = ttk.Frame(self.root)
        frame0.pack(anchor=tk.NW, fill=tk.X)
        lf = tk.LabelFrame(frame0, text='代理伺理器')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_item(lf, ('IP:', 'Port:'), ('host', 'port'))
        create_item(lf, ('帳號:', '密碼:'), ('identity', 'password'))
        self.password.config(show='*')
        proxy_enable = ttk.Checkbutton(lf, text='使用代理伺服器')
        proxy_enable.pack(anchor=tk.NW)
        proxy_enable.bind("<ButtonRelease-1>", self.proxy_enable_callback)

        lf = tk.LabelFrame(frame0, text='連線數量 (不超過8)')
        lf.pack(expand=True, fill=tk.X, padx=5, ipady=2, anchor=tk.NW)
        tk.Label(lf, text='單一網站最大連線數為1').pack(anchor=tk.NW)
        frame1 = ttk.Frame(lf)
        frame1.pack(expand=True, fill=tk.X, anchor=tk.NW)
        tk.Label(frame1, text='最多可同時連接網站數：').pack(side=tk.LEFT)
        max_number = tk.Entry(frame1)
        max_number.pack(side=tk.LEFT)
        self.register(max_number, self.number_filter, '%P')
        self.max_number = max_number
        self.proxy_enable = proxy_enable

        self.set_default()

    def set_default(self):
        set_text(self.max_number, GLOBAL.pool['size'])
        self.proxy_enable.state(('!alternate',))
        if GLOBAL.proxy['enable']:
            self.proxy_enable.state(('selected',))
        else:
            self.proxy_enable.state(('!selected',))

    def proxy_enable_callback(self, event):
        cbox = event.widget
        GLOBAL.proxy['enable'] = cbox.instate(('!selected',))

    def entry_callback(self, value, name):
        for key in self.keys:
            if str(getattr(self, key)) == name:
                GLOBAL.proxy[key] = value
                break
        return True

    def number_filter(self, value):
        if value.isdigit():
            p = int(value)
            if 0 < p <= 8:
                GLOBAL.pool['size'] = p
                return True
            return False
        return len(value) == 0


class OpenccSettings(Base):
    """* s2t: 簡體到繁體
* t2s: 繁體到簡體
* s2tw: 簡體到臺灣正體
* tw2s: 臺灣正體到簡體
* s2hk: 簡體到香港繁體（香港小學學習字詞表標準）
* hk2s: 香港繁體（香港小學學習字詞表標準）到簡體
* s2twp: 簡體到繁體（臺灣正體標準）並轉換為臺灣常用詞彙
* tw2sp: 繁體（臺灣正體標準）到簡體並轉換為中國大陸常用詞彙
* t2tw: 繁體（OpenCC 標準）到臺灣正體
* t2hk: 繁體（OpenCC 標準）到香港繁體（香港小學學習字詞表標準）
"""
    NA = '不使用'
    mapping = {NA: None}

    def create_view(self):
        super().create_view()
        lf = tk.LabelFrame(self.root, text='OpenCC')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        frame = ttk.Frame(lf)
        frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
        tk.Label(frame, text=self.__doc__, justify='left').pack(anchor=tk.NW)
        cb = ttk.Combobox(frame, state='readonly',
                          values=[self.NA, 's2t', 't2s', 's2tw', 'tw2s',
                                  's2hk', 'hk2s', 's2twp', 'tw2sp',
                                  't2tw', 't2hk',
                                  ])
        cb.pack(anchor=tk.NW)
        set_text(cb, GLOBAL.opencc)
        cb.bind("<<ComboboxSelected>>", self.callback)

    def callback(self, event):
        cb = event.widget
        text = cb.get()
        GLOBAL.opencc = self.mapping.get(text, text)


class SendTo(Base):
    def create_view(self):
        super().create_view()

        def create_item(root, text, key):
            frame = ttk.Frame(root)
            frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
            tk.Label(frame, text=text).pack(side=tk.LEFT)
            e = tk.Entry(frame)
            set_text(e, GLOBAL.mtp[key])
            e.pack(side=tk.LEFT, padx=5)
            vcmd = (e.register(getattr(self, f'{key}_callback')), '%P')
            e.config(validate='key', validatecommand=vcmd)

        lf = tk.LabelFrame(self.root, text='MTP')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_item(lf, '手機名:', 'device')
        create_item(lf, '手機內部路徑:', 'copyto')

    def device_callback(self, value):
        GLOBAL.mtp['device'] = value
        if value:
            GLOBAL.mtp['enable'] = True
            self.log('')
        else:
            self.log(f'缺少手機名，無法使用MTP')
            GLOBAL.mtp['enable'] = False
        return True

    def copyto_callback(self, value):
        GLOBAL.mtp['copyto'] = value
        if value:
            self.log('')
            GLOBAL.mtp['enable'] = True
        else:
            self.log(f'缺少手機內部路徑，無法使用MTP')
            GLOBAL.mtp['enable'] = False
        return True


class Others(Base):
    def create_view(self):
        super().create_view()

        def create_combo_item(root, text, values, key):
            frame = ttk.Frame(root)
            frame.pack(expand=True, fill=tk.X, anchor=tk.NW)
            tk.Label(frame, text=text).pack(side=tk.LEFT)
            cb = ttk.Combobox(frame, state='readonly',
                              values=values)
            cb.pack(side=tk.LEFT, padx=5)
            set_text(cb, str(GLOBAL.pygnoveldl[key]))
            cb.bind("<<ComboboxSelected>>", self.callback)
            setattr(self, key, cb)

        lf = lf = tk.LabelFrame(self.root, text=f'版本:{GLOBAL.version}')
        lf.pack(expand=True, fill=tk.X, anchor=tk.NW, padx=5)
        create_combo_item(lf, '開啟程式時，恢復上一次的任務:', [True, False], 'restore_mission')
        create_combo_item(lf, '自動移除已完成的任務:', [True, False], 'clean_finished')

    def callback(self, event):
        widget = event.widget
        for key in ['restore_mission', 'clean_finished']:
            if widget == getattr(self, key):
                GLOBAL.pygnoveldl[key] = eval(widget.get())
                break


class SettingsTab(ttk.Notebook):
    def __init__(self, main_window, master=None, **kw):
        super().__init__(master, **kw)
        self.main = main_window
        self.tabs = []
        self.create_view()

    def tab_change(self, event):
        widget = event.widget
        tab_id = widget.index(widget.select())
        obj = self.tabs[tab_id]
        if not obj.init:
            obj.create_view()

    def create_view(self):
        main_window = self.main
        self.bind("<<NotebookTabChanged>>", self.tab_change)

        d = {
            '環境': Environment,
            '網路': Network,
            '繁簡互換': OpenccSettings,
            '傳送到': SendTo,
            'pyGNovelDL': Others,
        }
        for text, cls in d.items():
            frame = ttk.Frame(self)
            self.add(frame, text=text)
            self.tabs.append(cls(main_window, frame))

