#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import json
import requests
from colorama import init, Fore, Style

URL = 'http://csearch.naver.com/dcontent/spellchecker.nhn'

def main(q):
    result = None

    params = {
        '_callback': 'window.__jindo2_callback._spellingCheck_0',
        'q': q,
    }
    response = requests.get(URL, params=params).text

    matched = re.search(r'.*?\((.*)\);', response)
    if matched:
        obj = json.loads(matched.group(1))
        result = obj['message']['result']
        print('errata_count : {}'.format(result['errata_count']))
        html = result['html']
        html = re.sub(r"<span class='re_red'>", Fore.RED, html)
        html = re.sub(r"<span class='re_green'>", Fore.GREEN, html)
        html = re.sub(r"<span class='re_purple'>", Fore.MAGENTA, html)
        html = re.sub(r'<\/?.*?>', Style.RESET_ALL, html)
        print('before : ' + q)
        print('after  : ' + html)
    else:
        print('no result.')

if __name__ == '__main__':
    try:
        q = sys.argv[1]
    except IndexError:
        sys.exit(1)

    init()
    main(q)

    print('')
    print('HELP : ', end='')
    print(Fore.RED + u'맞춤법 ' + Fore.GREEN + u'띄어쓰기 ' + Fore.MAGENTA + u'표준어 의심단어' + Style.RESET_ALL)

