#!/usr/bin/env python3

_description = '''
This is a quick and dirty Python script designed to simplify
the process of downloading videos to my phone that can then be
played through the podcast app. Eventually I intend to replace
this with my own custom podcast app. ... Eventually.

The script is basically a wrapper around yt-dlp, and yt-dlp
needs to be installed for it to work. 

Every time a download is attempted, the input used is written
into a timestamped "pass" or "fail" file, depending on the 
outcome of the operation. These files can become quite numerous 
over a fairly short period of time. Run the script without any 
arguments to blow away this detritus.

Run the script with the "-h" option for more information on how 
all the other bits and bobs work.
'''

from subprocess import run
from pathlib import Path
from shutil import which
from argparse import ArgumentParser
from datetime import datetime
from urllib.parse import urlparse
from tomllib import load as tomlload
from re import compile as mkrgx

def download_(_url, _cfg):
    '''Run yt-dlp with appropriate config file.
    Prints command line in dryrun mode.'''
    if _args.dryrun == True:
        print(f"yt-dlp --config-location {_cfg} {_url}")
    else:
        run(["yt-dlp", "--config-location", _cfg, _url], check=True)

def get_cfg_(_url):
    '''Return the location of the config file that matches
    the URL in the supplied line of input.'''
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
    '''Print a line of input to either the "pass" or "fail" file'''
    if _status == True: _file = _pass_file
    elif _status == False: _file = _fail_file
    else: raise Exception(f'Pass/Fail status must be a boolean.')
    with open(_file, "ta") as _f:
        _f.write(_url)

def clear_logs_():
    '''Delete "pass/fail/links/etc" files found in current directory. 
    Asks for user confirmation before deletion.'''
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
    '''Run through each line of input, download videos,
    and log "pass" or "fail" status.'''
    for _url in _urls:
        _url = _url.strip()
        try:
            download_(_url, get_cfg_(_url))
            log_(_url, True)
        except Exception as e:
            print(e)
            log_(_url, False)

def make_conf_():
    '''Read the toml file that maps yt-dlp config files to
    various website URLs and convert it into a dictionary.'''
    with open(_conf_file, "br") as _f:
        _conf = tomlload(_f)
    for _a in _conf:
        _b = str(_home_dir / _a)
        _conf[_b] = _conf.pop(_a)
    return _conf

def make_args_():
    '''Parse command line input and return an args object.'''
    _arg_parser = ArgumentParser(
        prog = "Temporary Video Grabbler",
        description = _description
    )
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
    return _arg_parser.parse_args()

def process_lists_(_list):
    '''Take a list of files, convert each one to an array of 
    lines, and send it off to another function for processing.'''
    for _i in _list:
        try:
            with open(_i, "tr") as _f:
                _x = _f.readlines()
            process_urls_(_x)
        except Exception as _e:
            print(_e)
            log_(str(_i), False)
        
'''
>>> SETUP
'''

'''Make sure yt-dlp can be found.'''
if which("yt-dlp") == None: exit(f'"yt-dlp" could not be found.')

'''Create Global Variables.'''
_timestamp = datetime.now().strftime("%y%m%d-%H%M%S")
_pass_file = f"0-pass-{_timestamp}"
_fail_file = f"0-fail-{_timestamp}"
_home_dir = Path(__file__).resolve(strict=True).parent
_conf_file = _home_dir / "config.toml"
_conf = make_conf_()
_args = make_args_()

'''
>>> RUN
'''

'''If there are no command line arguments, give the user the option 
to delete old log files; otherwise, parse input and download videos.'''
if len(_args.url) + len(_args.list) == 0:
    clear_logs_()
else:
    process_urls_(_args.url)
    process_lists_(_args.list)
