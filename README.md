# wiki_related_keyword_search
wikiの関連KW探索プログラム

## 実行環境構築

dokcerがinstallされている環境にてwiki_related_keyword_searchで以下のコマンドを実行

```
python main.py -t 探索するkw

python main.py -t 探索するkw


```

## 実行方法

wiki_related_keyword_search\srcで以下のコマンドを実行

```
python main.py -t 探索するkw
```

## 出力形式

探索KW順に出力される
ex)物流で探索した場合

```
-物流
    -英語$
    -ロジスティクス
        -英語$
        -原材料
            -英語$
            -製品$
        -生産
            -人間$
```


## 動作確認環境

- Python 3.7
- numpy 1.20.0
- pandas 1.1.5
