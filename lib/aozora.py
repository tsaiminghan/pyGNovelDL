from pathlib import Path
from .settings import YamlBase, conf_path


class Aozora(YamlBase):
    # linesep = os.linesep
    linesep = '\n'
    filename = conf_path / 'aozora.yaml'

    def __init__(self, textfile):
        self.load()
        self.fout = open(textfile, 'w', encoding='utf-8')
        self.text = ''

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fout:
            self.fout.close()

    def remove_ruby(self):
        self.text = self.text. \
            replace('》', self.DB_PARENTHESIS_END). \
            replace('《', self.DB_PARENTHESIS_START)

    def title(self, text):
        self.text += '{0}{1}{2}{3}{3}'.format(
            self.H2_START,
            text,
            self.H2_END,
            self.linesep)

    def change_page(self):
        self.text += self.CHANGE_PAGE + self.linesep
        self.remove_ruby()
        self.fout.write(self.text)
        self.text = ''

    def chapter(self, text):
        self.text += '{0}{6}{1}{2}{3}{4}{6}{5}{6}'.format(
            self.HCENTRAL,
            self.SHIFT_3,
            self.H1_START,
            text,
            self.H1_END,
            self.CHANGE_PAGE,
            self.linesep,
        )

    def paragraph(self, text):
        self.text += '{}{}{}'.format(
            self.INDENT,
            text,
            self.linesep)

    def bookinfo(self, url, author, bookname):
        fmt = '{0}{3}website:{3}<a href="{1}">{1}</a>{3}{0}{3}{2}{3}'
        intro = fmt.format(self.SEPARATOR_LINE,
                           url,
                           self.CHANGE_PAGE,
                           self.linesep)

        self.text += '{0}{3}{1}{3}{2}{3}'.format(
            bookname,
            author,
            intro,
            self.linesep)
