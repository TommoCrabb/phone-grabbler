#!/usr/bin/env python3

from subprocess import run
from pathlib import Path
from shutil import which
from argparse import ArgumentParser
from datetime import datetime
from urllib.parse import urlparse
from tomllib import load as tomlload
from re import fullmatch, compile as mkrgx

def download_(_url, _cfg):
    if _args.dryrun == True:
        print(f"yt-dlp --config-location {_cfg} {_url}")
    else:
        run(["yt-dlp", "--config-location", _cfg, _url], check=True)

def get_cfg_(_url):
    for _x in _conf:
        _a = urlparse(_url).netloc
        while True:
            try:
                if _a in _conf[_x]: return _x
                _a = _a.split(".", 1)[1]
            except:
                break
    raise Exception(f'No match found for url "{_url}"')

def log_(_url, _status):
    if _status == True: _file = _pass_file
    elif _status == False: _file = _fail_file
    else: raise Exception(f'Pass/Fail status must be a boolean.')
    with open(_file, "ta") as _f:
        _f.write(_url)

def clear_logs_():
    _a = []
    _r = mkrgx("0-(list|links|done|pass|fail).*")
    for _b in Path(".").iterdir():
        if _b.is_file() and _r.fullmatch(str(_b)):
            _a.append(_b)
    if len(_a) == 0: 
        print("No log files found.")
        return
    while True:
        print("\n==========\n")
        for _b in _a: print(str(_b))
        _i = input("\n==========\n\nWould you like to delete these files?\n\n(y/n): ")
        if _i == "n": return
        if _i == "y":
            print("")
            for _b in _a:
                try:
                    _b.unlink()
                    print(f"Deleted {_b}")
                except Exception as _e:
                    print(_e)
            print("")
            return

def process_urls_(_urls):
    for _url in _urls:
        _url = _url.strip()
        try:
            download_(_url, get_cfg_(_url))
            log_(_url, True)
        except Exception as e:
            print(e)
            log_(_url, False)

#############
### SETUP ###
#############

if which("yt-dlp") == None: exit(f'"yt-dlp" could not be found.')

_timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
_pass_file = f"0-pass-{_timestamp}"
_fail_file = f"0-fail-{_timestamp}"
_home_dir = Path(__file__).resolve(strict=True).parent
_conf_file = _home_dir / "config.toml"

with open(_conf_file, "br") as _f:
    _conf = tomlload(_f)

for _a in _conf:
    _b = str(_home_dir / _a)
    _conf[_b] = _conf.pop(_a)

################
### ARGPARSE ###
################

_arg_parser = ArgumentParser()
_arg_parser.add_argument(
    "-l","--list",
    nargs = 1,
    action = "extend",
    default = [],
    help = "A text file containing a list of URLS (one per line). Can be used multiple times."
)
_arg_parser.add_argument(
    "-d","--dryrun",
    action = "store_true",
    help = "Print yt-dlp commands without downloading anything."
)
_arg_parser.add_argument(
    "url",
    nargs = "*",
    action = "extend",
    help = "One or more URLS to download."
)
_args = _arg_parser.parse_args()

if len(_args.url) + len(_args.list) == 0:
    clear_logs_()
    exit()

process_urls_(_args.url)
for _i in _args.list:
    with open(_i, "tr") as _f:
        _x = _f.readlines()
    process_urls_(_x)