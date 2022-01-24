import sys
import os
import re
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
import argparse
import time


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
    time.sleep(1)
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

    kw_list = [kw+'$' if kw[-1] in no_target_search_flag else kw for kw in kw_list]

    keys = search_result.keys()
    kw_list = [kw+'@' if kw in keys else kw for kw in kw_list]

    return kw_list

def web_search(kw_list, kw_url_dict, search_result, limit_cnt):
    """
    対象KWのwikiの概要のリンクを探索しKWのdictを返す
    limit_cntが上限値に達するまで再帰で探索を行う

    Parameters
    ----------
    kw_list : list
        探索して取得したkwのlist

    kw_url_dict : dict
        探索するkwとそのkwのリンクを格納しているdict {'物流' : 'https://ja.wikipedia.org/wiki/%E7%89%A9%E6%B5%81', ...}

    search_result : dict
        探索元のKWと取得したKWのdict {'物流': ['英語$', 'ロジスティクス', ...], 'ロジスティクス':[...], ...}

    limit_cnt : int
        探索回数のカウント

    Returns
    -------
    search_result : dict
        探索元のKWと取得したKWのdict {'物流': ['英語$', 'ロジスティクス', ...], 'ロジスティクス':[...], ...}

    """
    next_search_kw_list = []
    next_search_url_dict = {}

    if kw_list:
        for kw in kw_list:
            if kw[-1] != '$' and kw[-1] != '@': # kwの末尾に$or@がついているkwは探索しない
                print(f'探索KW：{kw}')

                url = kw_url_dict[kw]
                r = get_web_page(url)
                kw_list_tmp, kw_url_dict_tmp = kw_scraping(r)
                kw_list_tmp = judgement_no_target_search(kw_list_tmp, search_result)
                
                print(f'取得したKWのlist：{kw_list_tmp}')
                search_result[kw] = kw_list_tmp
                next_search_kw_list += kw_list_tmp
                next_search_url_dict = kw_url_dict_tmp | next_search_url_dict

                limit_cnt += 1
                if limit_cnt >= search_limit_times:
                    return search_result

            else:
                pass
    
    else:
        print('探索対象が存在しません') # kw_listが空の場合は処理を抜ける
        return search_result

    return web_search(next_search_kw_list, next_search_url_dict, search_result, limit_cnt)

def search_result_conversion(search_result):
    """
    探索を未実施のKWに$を付与する

    Parameters
    ----------
    search_result : dict
        探索元のKWと取得したKWのdict {'物流': ['英語$', 'ロジスティクス', ...], 'ロジスティクス':[...], ...}

    Returns
    -------
    search_result : dict
        探索していないKWに$を付与したdict

    """

    search_result_tmp = {}

    for key in search_result.keys():
        result_list_tmp = []

        for result in search_result[key]:
            if result not in search_result.keys() and result[-1] not in search_unexecuted_flag:
                result_list_tmp.append(result+'$')
            else:
                result_list_tmp.append(result)

        search_result_tmp[key] = result_list_tmp

    return search_result_tmp

def search_result_output(search_result, parent_kw, depth_cnt):
    """
    探索結果をN分木で再帰的に出力する

    Parameters
    ----------
    search_result : dict
        探索元のKWと取得したKWのdict {'物流': ['英語$', 'ロジスティクス', ...], 'ロジスティクス':[...], ...}

    parent_kw : str
        探索元のKW

    depth_cnt : int
        探索の深さのカウント

    """

    print('    '*depth_cnt+'-'+parent_kw)
    depth_cnt = depth_cnt + 1

    for i, children_kw in enumerate(search_result[parent_kw]):

        if children_kw[-1] not in search_unexecuted_flag: # 末尾に$or@が付与されていないkwは探索結果を表示させる
            search_result_output(search_result, children_kw, depth_cnt)
        elif i != len(search_result[parent_kw])-1: # $or@が付与されていて表示してない探索kwが残っている場合はkwを表示するだけ
            print('    '*depth_cnt+'-'+children_kw)
        else:
            print('    '*depth_cnt+'-'+children_kw) # $or@が付与されていて表示してない探索kwが残っていない場合はkwを表示した後にreturnする
            return


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='wikiのKW探索PG')
    parser.add_argument('-t', '--target_kw', type=str, default=None, help='ターゲットKW')
    args = parser.parse_args()

    search_limit_times = 20 # 探索上限回数
    no_target_search_flag = ['語', '学'] # 探索しないKWの条件
    search_unexecuted_flag = ['@', '$'] # 探索未実施のkwに付与する値

    if args.target_kw is not None:

        kw_list = [args.target_kw]
        url_dict = {args.target_kw:'https://ja.wikipedia.org/wiki/'+urllib.parse.quote(args.target_kw)}
        search_result = web_search(kw_list, url_dict, search_result={}, limit_cnt=0)

        if len(search_result.keys()) == 1:
            print('探索対象が0件でした')
            sys.exit()

        search_result = search_result_conversion(search_result)

        search_result_output(search_result, parent_kw=args.target_kw, depth_cnt=0)

        out_put_path = '../data/'
        os.makedirs(os.path.dirname(out_put_path), exist_ok=True)
        with open(out_put_path+f'search_result_{args.target_kw}.json', 'w') as f:
            json.dump(search_result, f, ensure_ascii=False, indent=4)

    else:
        print('kw is None')