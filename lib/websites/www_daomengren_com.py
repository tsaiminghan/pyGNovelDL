from ._sample import NovelDL as Base

NAME = '盜夢人小說網'
NETLOC = 'www.daomengren.com'
REGEX = fr'(?<={NETLOC}/)(\d+_\d+)'

# OK in 2020/10/07
# http://www.daomengren.com/32_32281/
# http://www.daomengren.com/32_32281/20195239.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

    def find_timestamp(self, soup):
        # not support
        pass

