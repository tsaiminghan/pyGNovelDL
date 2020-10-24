from ._sample import NovelDL as Base

NAME = '頂點小說'
NETLOC = 'www.booktxt.net'
REGEX = f'(?<={NETLOC}/)([^/]+)'

# OK in 2020/10/07
# https://www.booktxt.net/2_2173/
# https://www.booktxt.net/2_2173/716921.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX
