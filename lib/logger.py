import logging.config
import yaml
from .settings import conf_path


class Logger(object):

    def init(self):
        conf = conf_path / 'logger.yaml'
        config = yaml.safe_load(conf.read_text())
        logging.config.dictConfig(config)
        self.logger = logging.getLogger('main')

    def exception(self, *args, **kw):
        self.logger.exception(*args, **kw)

    def debug(self, *args, **kw):
        self.logger.debug(*args, **kw)

    def error(self, *args, **kw):
        self.logger.error(*args, **kw)

    def info(self, *args, **kw):
        self.logger.info(*args, **kw)

    def warning(self, *args, **kw):
        self.logger.warning(*args, **kw)


logger = Logger()


