import requests
import time
from random import random
import re

retry_time = 3
retry_delay = 2
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}

'''
def callback(r, src_url, out_folder):
    filename = src_url.split('/')[-1]
    if not filename:
        filename = 'default.html'
    fd = Path(out_folder) / filename

    encoding = requests.utils.get_encoding_from_headers(r.headers)
    if encoding:
        r.encoding = encoding
        fd.write_text(r.text, encoding='utf-8')
    else:
        fd.write_bytes(r.content)
'''


class State(object):
    UNSET = -1
    FAIL = 0
    OK = 1
    RAW_EXIST = 2
    CONTENT_EXIST = 3


def charset(text):
    """
    charset="gbk"
    charset=gbk"
    """
    regex = '(?<=charset=)"*([^"]+)'
    ret = re.search(regex, text)
    if ret:
        return ret.group(1)


def set_charset(text, target='utf8'):
    c = charset(text)
    if c:
        return text.replace(f'charset={c}',
                            f'charset={target}', 1)
    return text


def proxies(host, port=80, identity=None, password=None, **_):
    d = {}
    account = ''
    if identity and password:
        account = f'{identity}:{password}@'

    for scheme in ['http', 'https']:
        d[scheme] = f'{scheme}://{account}{host}:{port}'
    return d


def download(url, **kwargs):
    kwargs = kwargs.copy()
    if not kwargs.get('headers'):
        kwargs['headers'] = headers

    r = None
    for _ in range(retry_time):
        try:
            r = requests.get(url, **kwargs)
            r.raise_for_status()
            if r.status_code == 200:
                content_length = r.headers.get("Content-Length")
                if content_length and int(content_length) != r.raw.tell():
                    raise Exception(
                        "incomplete response. Content-Length: {content_length}, got: {actual}"
                        .format(content_length=content_length, actual=r.raw.tell())
                    )
                break
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.HTTPError as errh:
            if r.status_code == 503:
                time.sleep(1 + random() * retry_delay)
                continue
            print("Http Error:", errh)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
        break
    else:
        print('error_code=', r.status_code)

    ok = r is not None and r.status_code == 200
    return ok, r
