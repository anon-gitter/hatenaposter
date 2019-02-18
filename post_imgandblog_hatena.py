#coding=utf-8
"""
特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします
"""
__author__ = "fftester06"
__status__ = "draft"
__version__ = "0.1"
__date__ = "Feb.19,2019"
#
# Filename:
# post_imageandblog_hatena.py
#
# 機能：
# 特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします。
#
# 使用方法：
# 下記フォーマットの設定ファイルをホームディレクトリに配置します
# (*Windowsの場合は、C:\Documents and Settings\<ユーザ名>)
#
# [base]
# api_key = abcdrfghij # <はてなブログのAPIキー>
# base_directory = C:\DOcuments and Settings\fftester06 # <画像ディレクトリのフルパス>
# username = fftester06 # はてなブログのユーザ名
# blogname = fftester06.hatenablog.com # はてなブログのブログ名
# draft = yes # 下書きならyes、公開するならno

import os
import sys
import random
import requests
import configparser
from datetime import date
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from hashlib import sha1
from pathlib import Path
from chardet.universaldetector import UniversalDetector
import re
from time import sleep
import shutil
import glob
import xml.etree.ElementTree as ET

# WSSE authentication
def wsse(username, api_key):
    created = datetime.now().isoformat() + "Z"
    b_nonce = sha1(str(random.random()).encode()).digest()
    b_digest = sha1(b_nonce + created.encode() + api_key.encode()).digest()
    c = 'UsernameToken Username="{0}", PasswordDigest="{1}", Nonce="{2}", Created="{3}"'
    return c.format(username, b64encode(b_digest).decode(), b64encode(b_nonce).decode(), created)

# Upload blog to hatena
def create_data_blog(title, body, username, draft):

    template = """<?xml version="1.0" encoding="utf-8"?>
    <entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
    <title>{0}</title>
    <author><name>{1}</name></author>
    <content type="text/x-markdown">
{2}
    </content>
    <updated>{3}</updated>
    <category term="" />
    <app:control>
    <app:draft>{4}</app:draft>
    </app:control>
    </entry>
    """

    now = datetime.now()
    dtime = str(now.year)+"""-"""+str(now.month)+"""-"""+str(now.day)+"""T"""+str(now.hour)+""":"""+str(now.minute)+""":"""+str(now.second)
    data = template.format(title, username, body, dtime, draft).encode()
    return data

def check_encoding(file):
    detector = UniversalDetector()
    with open(file, mode='rb') as f:
        for binary in f:
            detector.feed(binary)
            if detector.done:
                break
    detector.close()
    charset = detector.result['encoding']
    return charset

def post_hatena(data, headers, username, blogname):
    url = 'http://blog.hatena.ne.jp/{0}/{1}/atom/entry'.format(username, blogname)
    r = requests.post(url, data=data, headers=headers)

    if r.status_code != 201:
        sys.stderr.write('Error!\n' + 'status_code: ' + str(r.status_code) + '\n' + 'message: ' + r.text)


# Upload images to hatena foto life
def create_data_foto(filename):
    infile = open(filename, 'rb')
    files = infile.read()
    ext = Path(filename).suffix
    ext = ext[1:]
    if ext == "jpg":
        ext = "jpeg"

    uploadData = b64encode(files)

    template="""
    <entry xmlns="http://purl.org/atom/ns#">
    <title>{0}</title>
    <content mode="base64" type="image/{1}">{2}</content>
    </entry>
    """

    imgname = os.path.basename(filename)[3:]
    return template.format(imgname,ext,uploadData.decode())

def upload_foto(data, headers):
    url = 'http://f.hatena.ne.jp/atom/post/'
    r = requests.post(url, data=data, headers=headers)
    uploaded  = False
    fotolink = None

    if r.status_code != 201:
        sys.stderr.write('Upload error!\n' + 'status_code: ' + str(r.status_code) + '\n' + 'message: ' + r.text)
    else:
        uploaded = True
        root = ET.fromstring(r.text)
        for syntax in root.findall('{http://www.hatena.ne.jp/info/xmlns#}syntax'):
            fotolink = syntax.text

    return fotolink


def foto_info(headers):
    url = 'http://f.hatena.ne.jp/atom/feed/'
    r = requests.post(url, headers=headers)

    return re.search('[0-9]{14}', r.text).group()

def read_config():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/hatenaposterConfig.txt'), 'UTF-8')

    apikey = config.get('base','api_key')
    base_directory = config.get('base','base_directory')
    username = config.get('base','username')
    blogname = config.get('base','blogname')
    draft = config.get('base','draft')

    # Windowsパスで\が用いられている場合、\\に変換
    base_directory_r = repr(base_directory).replace("'", "")
    
    return apikey, base_directory_r, username, blogname, draft    

# -----------------------------------------------------------
# Main function

def main():

    # define WSSE header
    api_key, base_directory, username, blogname, draft = read_config()
    headers = {'X-WSSE': wsse(username, api_key)}

    yesterday = (date.today() + timedelta(days=-1)).strftime("%y%m%d") # 昨日の日付文字列を作成
    filenames = glob.glob(base_directory + "/???" + yesterday + "*") # 昨日の日付を含むファイル名を取得
    fotolinks = ""
    for filename in filenames:
        data_foto = create_data_foto(filename)
        fotolink = upload_foto(data_foto, headers)
        sleep(5)
        if (fotolink is not None):
            fotolinks += ( fotolink + "\n" )
            
    if (fotolinks == ""):
        print("No photos to upload.")
    else:
        body = fotolinks
        title = (date.today() + timedelta(days=-1))
        data_blog = create_data_blog(title, body, username, draft)
        post_hatena(data_blog, headers, username, blogname)
        
    print('Done')

if __name__ == '__main__':
    main()
