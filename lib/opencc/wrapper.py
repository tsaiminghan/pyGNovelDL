import sys
from pathlib import Path
import opencc.opencc
from opencc.opencc import OpenCC as Base


class OpenCC(Base):
    def __init__(self, conversion):
        if hasattr(sys, 'frozen'):
            # Handles PyInstaller
            opencc.opencc.__file__ = Path(sys.executable).parent / 'opencc' / 'xxx.py'
        else:
            opencc.opencc.__file__ = __file__
        super().__init__(conversion=conversion)
