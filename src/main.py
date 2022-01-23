import os
import re
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
import argparse
import time
import pprint


def get_web_page(url):
    """
    対象URLのHTMLを取得

    Parameters
    ----------
    url : str
        探索対象のURL

    Returns
    -------
    r : requests.models.Response
        URL先のHTML
    
    """
    r = requests.get(url)  
    r.encoding = r.apparent_encoding
    print(type(r))
    return r

def kw_scraping(r):
    """
    取得したHTMLから対象KWとurlをスクレイピング

    Parameters
    ----------
    r : str
        URL先のHTML

    Returns
    -------
    kw_list : list
        探索して取得したkwのlist

    url_dict : dict
        次の探索先のdict {'物流':'https://ja.wikipedia.org/wiki/物流', ....}

    """
    kw_list = []
    url_dict = {}
    soup = BeautifulSoup(r.text, "html.parser")

    try:
        soup = soup.select('#mw-content-text > div.mw-parser-output > p')[0]

        for a in soup.find_all(href=re.compile("/wiki/")):

            if re.match(r'<a href="/wiki/.*</a>', str(a)):
                kw = re.sub('/wiki/', '', urllib.parse.unquote(a.attrs['href']))
                kw_list.append(kw)
                url_dict[kw] = 'https://ja.wikipedia.org' + a.attrs['href']
            
            else:
                print('不正なKWを取得しました')

    except IndexError:
        print('対象KWがありません')
        pass

    return kw_list, url_dict

def judgement_no_target_search(kw_list, search_result):
    """
    取得したKWに探索対象外の情報を付与する
    末尾が語と学のKW ⇒ $を付与
    search_resultに含まれるKW ⇒ @を付与 

    Parameters
    ----------
    kw_list : list
        探索して取得したkwのlist

    search_result : dict
        探索元のKWと取得したKWのdict {'物流': ['英語$', 'ロジスティクス', ...], 'ロジスティクス':[...], ...}

    Returns
    -------
    kw_list : list
        探索対象外の情報が付与されたkwのkist

    """

    no_tagert_list = ['語', '学']
    kw_list = [kw+'$' if kw[-1] in no_tagert_list else kw for kw in kw_list]

    keys = search_result.keys()
    kw_list = [kw+'@' if kw in keys else kw for kw in kw_list]

    return kw_list


def web_search(kw_list, kw_url_dict, search_result, limit_cnt):
    next_search_kw_list = []
    next_search_url_dict = {}

    for kw in kw_list:
        if kw[-1] != '$' and kw[-1] != '@': # kwの末尾に$or@がついているkwは探索しない
            print(kw)
            url = kw_url_dict[kw]
            r = get_web_page(url)
            kw_list_tmp, kw_url_dict_tmp = kw_scraping(r)
            kw_list_tmp = judgement_no_target_search(kw_list_tmp, search_result)
            print(kw_list_tmp)
            search_result[kw] = kw_list_tmp
            next_search_kw_list += kw_list_tmp
            next_search_url_dict = kw_url_dict_tmp | next_search_url_dict

            limit_cnt += 1
            if limit_cnt >= 10:
                return search_result

            time.sleep(1)

        else:
            pass

    return web_search(next_search_kw_list, next_search_url_dict, search_result, limit_cnt)

def search_result_conversion(search_result):

    search_result_tmp = {}
    no_conversion_list = ['@', '$']

    for key in search_result.keys():
        result_list_tmp = []

        for result in search_result[key]:
            if result not in search_result.keys() and result[-1] not in no_conversion_list:
                result_list_tmp.append(result+'$')
            else:
                result_list_tmp.append(result)

        search_result_tmp[key] = result_list_tmp

    return search_result_tmp

def tree_display(search_result, parent_kw, cnt):
    print('  '*cnt+'-'+parent_kw)
    cnt = cnt + 1

    for i, children_kw in enumerate(search_result[parent_kw]):
        if children_kw[-1] not in ['@', '$']:
            tree_display(search_result, children_kw, cnt)
        elif i != len(search_result[parent_kw])-1:
            print('  '*cnt+'-'+children_kw)
        else:
            print('  '*cnt+'-'+children_kw)
            return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='wikiのKW探索PG')
    parser.add_argument('-t', '--target_kw', type=str, default=None, help='ターゲットKW')
    args = parser.parse_args()

    if args.target_kw is not None:

        kw_list = [args.target_kw]
        url_dict = {args.target_kw:'https://ja.wikipedia.org/wiki/'+urllib.parse.quote(args.target_kw)}
        search_result = web_search(kw_list, url_dict, search_result={}, limit_cnt=0)
        search_result = search_result_conversion(search_result)

        tree_display(search_result, parent_kw=args.target_kw, cnt=0)

        out_put_path = '../data/'
        os.makedirs(os.path.dirname(out_put_path), exist_ok=True)
        with open(out_put_path+f'search_result_{args.target_kw}.json', 'w') as f:
            json.dump(search_result, f, ensure_ascii=False, indent=4)

    else:
        print('kw is None')

