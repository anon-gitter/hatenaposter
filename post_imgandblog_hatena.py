#coding=utf-8
"""
特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします
"""
__author__ = "fftester06"
__status__ = "draft"
__version__ = "0.1"
__date__ = "Feb.16,2019"
#
# Filename:
# post_imageandblog_hatena.py
#
# 機能：
# 特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします。
# 
# 使用方法：
# はてなブログのAPI KEYを平文テキストで一行記載したものを、apikey.txtとして
# ホームディレクトリに配置します
# (*Windowsの場合は、C:\Documents and Settings\<ユーザ名>)
#

import os
import sys
import random
import requests
from base64 import b64encode
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from chardet.universaldetector import UniversalDetector
import re
from time import sleep
import shutil
import glob

now = datetime.now()
dtime = str(now.year)+"""-"""+str(now.month)+"""-"""+str(now.day)+"""T"""+str(now.hour)+""":"""+str(now.minute)+""":"""+str(now.second)
print(dtime)

# setting -----------------------------------------------------------                                                                                                                                       
username = 'fftester06'
blogname = 'fftester06.hatenablog.com'
draft = 'yes' # yes or no    下書きとして投稿する場合はyes。本投稿はno。                                                                                                                                                                               

# WSSE authentication
def wsse(username, api_key):
    created = datetime.now().isoformat() + "Z"
    b_nonce = sha1(str(random.random()).encode()).digest()
    b_digest = sha1(b_nonce + created.encode() + api_key.encode()).digest()
    c = 'UsernameToken Username="{0}", PasswordDigest="{1}", Nonce="{2}", Created="{3}"'
    return c.format(username, b64encode(b_digest).decode(), b64encode(b_nonce).decode(), created)

# Upload blog to hatena
def create_data_blog(title, body, fotoname):
    if fotoname == None:
        text = body
    else:
        text = body + """                                                                                                                                                                                   
                                                                                                                                                                                                            
[f:id:{0}:{1}j:plain]                                                                                                                                                                                     
        """.format(username, fotoname)

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

    data = template.format(title, username, text, dtime, draft).encode()
    return data

def parse_text(file, charset):
    with open(file, encoding=charset) as f:
        obj = f.readlines()
        body  = ""
        for i, line in enumerate(obj):
            body = body + line
    return body

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

def post_hatena(data, headers):
    url = 'http://blog.hatena.ne.jp/{0}/{1}/atom/entry'.format(username, blogname)
    r = requests.post(url, data=data, headers=headers)

    if r.status_code != 201:
        sys.stderr.write('Error!\n' + 'status_code: ' + str(r.status_code) + '\n' + 'message: ' + r.text)


# Upload images to hatena foto life
def create_data_foto(filename):
    infile = filename.open('rb')
    files = infile.read()
    ext = filename.suffix
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

    return template.format(filename,ext,uploadData.decode())

def upload_foto(data, headers):
    url = 'http://f.hatena.ne.jp/atom/post/'
    r = requests.post(url, data=data, headers=headers)

    if r.status_code != 201:
        sys.stderr.write('Upload error!\n' + 'status_code: ' + str(r.status_code) + '\n' + 'message: ' + r.text)

def foto_info(headers):
    url = 'http://f.hatena.ne.jp/atom/feed/'
    r = requests.post(url, headers=headers)

    return re.search('[0-9]{14}', r.text).group()

def read_api_key():
    api_key_file = open(os.path.expanduser('~/apikey.txt'), "r")
    return api_key_file.read()

# -----------------------------------------------------------                                                                                                                                          
# Main function

def main():

    # define WSSE header
    api_key = read_api_key
    headers = {'X-WSSE': wsse(username, api_key)}
    
    # とりあえずシンプルに画像ポストのテスト

    filename = Path('C:/Documents and Settings/ss/My Documents/ffxiss/ffxiuser/screenshots/Zan190214002021a.jpg')
    data_foto = create_data_foto(filename)

    # upload_foto(data_foto, headers)
    # sleep(10)

    fotoflag = 1
    print('---- Uploaded foto info ----')
    fotoname = foto_info(headers)
    print(fotoname)

    # ブログの方もシンプルにポスト
    # まずは定型文を付加するだけに、のちのち拡張予定

    # filename_log = 'C:/Documents and Settings/ss/My Documents/ffxiss/ffxiuser/screenshots/Zan190214002021a.log'
    # charset = check_encoding(filename_log)
    # body = parse_text(filename_log, charset)
    body = ""
    title = '今日のSS'
    data_blog = create_data_blog(title, body, fotoname)

    # post_hatena(data_blog, headers)
    print('Done')

if __name__ == '__main__':
    main()
