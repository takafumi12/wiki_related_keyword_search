import os
import re
import sys
import requests
import urllib.parse
from bs4 import BeautifulSoup
import argparse


def get_web_page(url):
    r = requests.get(url)  # URLで指定したWebページを取得する。
    r.encoding = r.apparent_encoding  # バイト列の特徴から推定したエンコーディングを使用する。
    print(f'encoding: {r.encoding}', file=sys.stderr)  # エンコーディングを標準エラー出力に出力する。
    print(r.text)  # デコードしたレスポンスボディを標準出力に出力する。
    return r

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='wikiのKW探索PG')
    
    parser.add_argument('-t', '--target_kw', type=str, default=None, help='ターゲットKW')

    args = parser.parse_args()

    if args.target_kw is not None:
        url = 'https://ja.wikipedia.org/wiki/'+urllib.parse.quote(args.target_kw)
        r = get_web_page(url)
        print(r)
        
    else:
        print('kw is None')

