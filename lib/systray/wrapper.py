from infi.systray import SysTrayIcon as Base


class SysTrayIcon(Base):
    def __init__(self,
                 icon,
                 hover_text,
                 menu_options=None,
                 on_quit=None,
                 default_menu_index=None,
                 window_class_name=None):
        super().__init__(icon, hover_text, menu_options,
                         on_quit, default_menu_index, window_class_name)
        # change 'QUIT' to '還原'
        ret = self._menu_options[0]
        self._menu_options[0] = ('還原', *ret[1:])
