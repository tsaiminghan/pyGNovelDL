from ._sample import NovelDL as Base

NAME = '燃文小說'
NETLOC = 'www.ranwen.la'
REGEX = fr'(?<={NETLOC}/)(files/article/\d+/\d+)'

# OK in 2020/10/07
# https://www.ranwen.la/files/article/89/89698/
# https://www.ranwen.la/files/article/89/89698/99664594.html


class NovelDL(Base):
    name = NAME
    netloc = NETLOC
    regex = REGEX

