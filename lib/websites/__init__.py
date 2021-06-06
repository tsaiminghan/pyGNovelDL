from pathlib import Path
from urllib import parse
from . import book_qidian_com
from . import tw_aixdzs_com
from . import www_35xs_co
from . import www_50zw_net
from . import www_67shu_net
from . import www_230book_com
from . import www_b5200_net
from . import www_booktxt_net
from . import www_ck101_org
from . import www_daomengren_com
from . import www_iqiwx_com
from . import www_kssw_net
from . import www_luoqiuzw_com
from . import www_ptwxz_com
from . import www_ranwen_la
from . import www_shumil_co
from . import www_twfanti_com
from . import www_xiaoshuo_cc
from . import www_xinwanben_com
from . import www_xssilu_com
from . import www_yunlaige_net
from . import www_zhaishuyuan_com
from . import www_zzdxss_com
from ..modloader import ModLoader


class Loader(ModLoader):
    def __init__(self):
        self.mod_list = [
            book_qidian_com,
            tw_aixdzs_com,
            www_230book_com,
            www_35xs_co,
            www_50zw_net,
            www_67shu_net,
            www_b5200_net,
            www_booktxt_net,
            www_ck101_org,
            www_daomengren_com,
            www_iqiwx_com,
            www_kssw_net,
            www_luoqiuzw_com,
            www_ptwxz_com,
            www_ranwen_la,
            www_shumil_co,
            www_twfanti_com,
            www_xiaoshuo_cc,
            www_xinwanben_com,
            www_xssilu_com,
            www_yunlaige_net,
            www_zhaishuyuan_com,
            www_zzdxss_com,
        ]

    @staticmethod
    def compare(mod, value):
        return mod.NETLOC == value

    def get_mod(self, url):
        netloc = parse.urlparse(url).netloc
        if not netloc:
            # for debug message
            netloc = url
        return super().get_mod(netloc).NovelDL(url)


_mod = Loader()
get_mod = _mod.get_mod
