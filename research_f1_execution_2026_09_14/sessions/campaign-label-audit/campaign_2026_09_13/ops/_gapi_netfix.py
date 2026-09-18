"""Net-fix wrapper for the google-workspace ops on this host.

Why: this machine's IPv6 connectivity is flaky (most AAAA addresses time out), and
httplib2 (used by google_api.py / google_auth_httplib2) sticks to the first resolved
address without fast fallback -> WinError 10060. curl is fine because of Happy Eyeballs.

This wrapper (a) disables httplib2's win32/env proxy detection and (b) sorts
getaddrinfo results IPv4-first, then runs the stock google_api.py unchanged.

Usage:  python _gapi_netfix.py drive search "llmzip" --max 5
"""
import socket
import sys
import runpy

import httplib2

httplib2.proxy_info_from_environment = lambda *a, **k: None
httplib2.proxy_info_from_win32 = lambda *a, **k: None

_orig_gai = socket.getaddrinfo


def _gai(host, port, family=0, type=0, proto=0, flags=0):
    res = _orig_gai(host, port, family, type, proto, flags)
    res.sort(key=lambda r: r[0] != socket.AF_INET)  # IPv4 first
    return res


socket.getaddrinfo = _gai

TARGET = r"C:\Users\MDP\AppData\Local\hermes\skills\productivity\google-workspace\scripts\google_api.py"
sys.argv = [TARGET] + sys.argv[1:]
runpy.run_path(TARGET, run_name="__main__")