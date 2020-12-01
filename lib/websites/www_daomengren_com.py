from ._sample import NovelDL as Base

NAME = '盜夢人小說網'
NETLOC = 'www.daomengren.com'
REGEX = fr'(?<={NETLOC}/)(\d+_\d+)'

OPTIONS = {
    'download': {
        'verify': False
    },
}

# OK in 2020/12/01
# http://www.daomengren.com/32_32281/
# http://www.daomengren.com/32_32281/20195239.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
    options = OPTIONS

    def find_timestamp(self, soup):
        # not support
        pass

