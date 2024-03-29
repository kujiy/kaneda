import re
import sys

import requests, json
import random, os
from emoji_list import emoji_list

from bs4 import BeautifulSoup, SoupStrainer

from env import env

_NUL = object()  # unique value guaranteed to never be in JSON data

FILE = "last-pdf.txt"


def rec_find(key, val, obj):
    """ Recursively find all the values of key in all the dictionaries in obj
        with a "type" key equal to kind.
    """
    if isinstance(obj, dict):
        key_value = obj.get(key, _NUL)  # _NUL if key not present
        if key_value is not _NUL and obj.get(key) == val:
            yield obj
        for jsonkey in obj:
            jsonvalue = obj[jsonkey]
            for v in rec_find(key, val, jsonvalue):  # recursive
                yield v
    elif isinstance(obj, list):
        for item in obj:
            for v in rec_find(key, val, item):  # recursive
                yield v


def start():
    ## 1. kaneda topからlink href を引っこ抜く
    ## 2. link hrefからjsonをfetch. その中に pdf url がある

    # 1.Web 情報取得
    top_content = requests.get('https://www.kanedasc.com/%E5%85%A5%E4%BC%9A%E3%81%AE%E6%B5%81%E3%82%8C')
    # BeautifulSoup オブジェクトを作成
    soup = BeautifulSoup(top_content.text, "html.parser", parse_only=SoupStrainer('link'))

    # print(soup.prettify())

    features_masterPage = soup.find_all('a', attrs={'data-testid' : "linkElement"})

    # 2. pdf url jsonを取得
    json_url = features_masterPage[0]["href"]
    json_content = requests.get(json_url)
    json_file = json.loads(json_content.text)
    pdf_obj = rec_find("label", '空席状況', json_file['props']['render']['compProps'])

    pdf_url = None
    # get generator(yield) object
    for text in pdf_obj:
        pdf_url = text["link"]["href"]
        print("<---------------------------------- pdf is found.")

    if pdf_url is not None:
        update_handler(pdf_url)
        sys.exit()

    # 2021/02~~~~
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if current_link.endswith('pdf'):
            print('Tengo un pdf: ' + current_link)
            print(link.text)
            if re.findall("空", link.text):
                pdf_url = current_link
                print("<---------------------------------- pdf is found.")

    if pdf_url is not None:
        update_handler(pdf_url)
        sys.exit()

    print("pdf was not found.")


random.shuffle(emoji_list)
picked = emoji_list[0]


def fetch_emoji():
    out = ""
    for i in range(3):
        out += picked
    return out


def update_handler(text):
    if text == open(FILE).read():
        print('no change')
        return
    else:
        print('updated!')

    with open(FILE, 'w') as filetowrite:
        filetowrite.write(text)
    emoji = fetch_emoji()
    sendtext = f"\n{emoji} 金田さん更新！ {emoji}\n{text}\n{emoji}{emoji}{emoji}{emoji}"

    print(sendtext)
    line(sendtext)


def line(str):
    from linenotipy import Line
    line = Line(token=env.LINE_TOKEN)
    line.post(message=str)


if __name__ == "__main__":
    start()
