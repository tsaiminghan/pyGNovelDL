import threading
from .mission import Mission
from .download import State as DLState
from .settings import GLOBAL, YamlBase, conf_path
from .logger import logger


class MissionMgr(object):
    lock = threading.Lock()
    running_lock = threading.Lock()
    _mid = 0
    _running = 0
    yamlfile = conf_path / 'missions.yaml'

    def __init__(self, main_window):
        self.table = main_window.mission_tab.table
        self.current = main_window.current
        self.pool = main_window.pool
        self.worker = main_window.worker
        self.missions = {}
        self._netloc_usage = {}

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def save(self):
        lst = []
        for mission in self.missions.values():
            mission.book_dump()
            d = mission.todict()
            if d['keys']:
                lst.append(d)
        yaml = YamlBase(self.yamlfile)
        yaml.dumps(data=lst)

    def load(self):
        """ assume the database of toc_url must exists """
        yaml = YamlBase(self.yamlfile)
        if yaml.load():
            for data in yaml.data:
                toc_url = data['toc_url']
                keys = data['keys']
                mission = self.get_lock(toc_url, load=True)
                self.current.put_normal('MISSION_ADD', mission, keys)

    def get_lock(self, url, load=False):
        """ get mission """
        with self.lock:
            m = Mission(url, load=load)
            toc_url = m.book.mod.toc_url
            ret = self.missions.get(toc_url, m)
            if ret is m:
                self._mid += 1
                m.set_mid(self._mid)
                self.missions[toc_url] = m
                m.load()
            return ret

    def put_lock(self, toc_url):
        """ release mission """
        with self.lock:
            if toc_url in self.missions:
                mission = self.missions.pop(toc_url)
                self.netloc_usage_remove(mission)
                return mission

    def add(self, mission, *, key):
        """ add tree item, sync mission usage """
        if mission == key:
            if ret := self.table.add(mission.parent_item(), key=key):
                mission.usage.new()
        else:
            tree_key = mission.to_key(key)
            item = mission.child_item(key)
            if ret := self.table.add(item, parent=mission, key=tree_key):
                mission.usage.set_lock(INIT=tree_key)
        return ret

    def remove(self, mission, *, key):
        """ remove tree item, sync mission usage """
        if mission == key:
            mission.usage.new()
            self.table.remove(*self.table.get_children(mission))
            self.table.remove(mission)
        else:
            self.table.remove(key)
            mission.usage.remove_lock(key)

    def update_state(self, mission, tree_key, state):
        text = mission.usage.get_text(state)
        if mission is not tree_key:
            mission.usage.set_lock(state, tree_key)
        self.current.put_normal('UPDATE_ITEM', tree_key, state=text)

    def netloc_usage_list(self, mission):
        netloc = mission.book.mod.netloc
        ret = self._netloc_usage.get(netloc, [])
        self._netloc_usage[netloc] = ret
        return ret

    def netloc_usage_add(self, mission):
        ret = self.netloc_usage_list(mission)
        if mission not in ret:
            ret.append(mission)

    def netloc_usage_remove(self, mission):
        ret = self.netloc_usage_list(mission)
        if mission in ret:
            ret.remove(mission)

    def net_usage_remove_lock(self, mission):
        with self.lock:
            self.netloc_usage_remove(mission)

    def get_download_item_lock(self):
        with self.lock:
            table = self.table
            for mission in table.get_children():
                if len(mission.usage['DOWNLOAD']) > 0:
                    continue
                if len(self.netloc_usage_list(mission)) > 0:
                    continue
                if mission.usage['READY']:
                    self.netloc_usage_add(mission)
                    return mission, mission.usage['READY'][0]
        return None, None

    def _mission_remove(self, tree_key):
        mission = self.table.parent(tree_key)
        if mission:
            self.remove(mission, key=tree_key)
        else:
            mission = tree_key
            logger.debug('MISSION_REMOVE %s', mission.name)
            self.remove(mission, key=mission)
            self.current.put_normal('LOG_MESSAGE', f'移除任務: {mission.name}')

    def delete(self, toc_url):
        mission = self.get_lock(toc_url)
        self.put_lock(toc_url)
        mission.delete()
        if mission.usage['ALL']:
            self._mission_remove(mission)

    def register(self):
        @self.worker.register('RESTORE_FAIL')
        def _():
            for mission in self.table.get_children():
                tree_keys = mission.usage['FAIL'].copy()
                for tree_key in tree_keys:
                    self.update_state(mission, tree_key, state='READY')

        @self.current.register('MISSION_REMOVE')
        def _(tree_key):
            self._mission_remove(tree_key)

        @self.current.register('MISSION_ADD')
        def _(mission, keys):
            logger.debug('MISSION_ADD START %s', mission.name)
            new_keys = []
            self.add(mission, key=mission)
            for k in keys:
                if self.add(mission, key=k):
                    new_keys.append(k)
            if new_keys:
                self.worker.put_normal('MISSION_INIT', mission, new_keys)
            logger.debug('MISSION_ADD END %s', mission.name)

        @self.worker.register('RESTORE_MISSIONS')
        def _():
            if GLOBAL.pygnoveldl['restore_mission']:
                self.load()

        @self.worker.register('MISSION_INIT')
        def _(mission, keys):
            logger.debug('MISSION_INIT START %s', mission.name)
            for key in keys:
                tree_key = mission.to_key(key)
                if mission.book.content_file(key).exists():
                    mission.book.chapters[key]['state'] = DLState.CONTENT_EXIST
                    mission.dirty = True
                    state = 'OK'
                else:
                    state = 'READY'
                self.update_state(mission, tree_key, state)
            self.current.put_normal('UPDATE_PARENT', mission)
            self.current.put_normal('LOG_MESSAGE', f'加入任務: {mission.book.name}')
            logger.debug('MISSION_INIT END %s', mission.name)

        @self.current.register('UPDATE_PARENT')
        def _(mission, **kw):
            table = self.table
            if not table.exists(mission):
                return
            name = table.set(mission, 'name').rpartition(' ')[0]
            count = len(mission.usage['OK'])
            total = len(table.get_children(mission))
            new_name = f'{name} ({count}/{total})'
            if state := kw.get('state'):
                kw['state'] = mission.usage.get_text(state)
            else:
                """ TODO: set the state """
                if total == count:
                    kw['state'] = mission.usage.get_text('OK')
                elif len(mission.usage['INIT']) > 0:
                    kw['state'] = mission.usage.get_text('INIT')
                elif len(mission.usage['DOWNLOAD']) > 0:
                    kw['state'] = mission.usage.get_text('DOWNLOAD')
                elif len(mission.usage['READY']) > 0:
                    kw['state'] = mission.usage.get_text('READY')
                else:
                    kw['state'] = mission.usage.get_text('FAIL')

            table.update(mission, name=new_name, **kw)

        @self.current.register('UPDATE_ITEM')
        def _(key, **kw):
            self.table.update(key, **kw)


