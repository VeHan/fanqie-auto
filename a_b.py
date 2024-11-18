import subprocess
from functools import partial
subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")
import execjs

from utils import readfile

ab_js_txt = readfile('420ab.js')

ab_js = execjs.compile(ab_js_txt)

def get_ab(params, body, ua):
    ret = ab_js.call("get_ab",params, body, ua )
    return ret