from os import walk
from zipfile import ZipFile
import re
from bs4 import BeautifulSoup
import pandas as pd


def main(path='.'):
    file_list = []
    for (dirpath, dirnames, filenames) in walk(path):
        for f in filenames:
            if '.epub' not in f:
                break
            file_list.append(f'{dirpath}/{f}')
    return file_list


def unzip(files):
    cnt = 0
    title_list = []
    text_list = []
    for f in files:
        title = ''
        texts = []
        try:
            zip = ZipFile(f)
            is_ok = False
            for info in zip.infolist():
                if 'content.opf' in info.filename:
                    is_tit = True
                    #print(info.filename)
                    html = BeautifulSoup(str(zip.read(info.filename), 'utf-8'))
                    title = html.find('dc:title').get_text(strip=True)
                if re.match(r'index_split_.*.html$', info.filename) and info.filename != 'index_split_000.html':
                    #print(info.filename)
                    html2 = BeautifulSoup(str(zip.read(info.filename), 'utf-8'))
                    for element in html2.body.findAll('p'):
                        if len(element.get_text(strip=True)) == 0:
                            continue
                        texts.append(element.get_text(strip=True))
                if re.match(r'.*Section.*.xhtml$', info.filename):
                    #print(info.filename)
                    html2 = BeautifulSoup(str(zip.read(info.filename), 'utf-8'))
                    for element in html2.body.findAll('p'):
                        if len(element.get_text(strip=True)) == 0:
                            continue
                        texts.append(element.get_text(strip=True))
            if not is_tit:
                print(f'ERR2: {f}')
                continue
            else:
                title_list.append(title)
                text_list.append(' '.join(texts))
        except Exception as ex:
            print(f'ERR: {f}')
        cnt += 1
        if cnt % 500 == 0:
            print(f'# {cnt} contents processing...')
    return title_list, text_list


def save_file(title_list, text_list, f_name='res.pkl'):
    df = pd.DataFrame({'title': title_list, 'text': text_list})
    df.to_pickle(f_name)


if __name__ == '__main__':
    files = main()
    title_list, text_list = unzip(files)
    save_file(title_list, text_list)
    if False:
        cnt = 0
        for title, text in zip(title_list, text_list):
            print(f'=========== {cnt} ===========')
            print(f'## TITLE = {title}')
            print(f'## TEXT = {text}')
            print()
            cnt += 1
