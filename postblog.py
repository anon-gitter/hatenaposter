# coding=utf-8


"""
特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします
"""

__author__ = "fftester06"
__status__ = "draft"
__version__ = "0.1"
__date__ = "Feb.19,2019"

#
# Filename:
# postblog.py
#
# 機能：
# 特定のディレクトリの画像を、WebAPIを用いてはてなブログ、はてなフォトライフにアップします。
#
# 使用方法：
# 下記フォーマットの設定ファイルを本ファイルと同じディレクトリに配置します
#
# ※はてなブログのAPIキーは、ブログの設定→詳細設定→Atompubにあります（下の方）
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
import picktimestr

class Hatenaposter(object):
    
    def __init__(self):
        pass
    
    # WSSE authentication
    def wsse(self, username, api_key):
        created = datetime.now().isoformat() + "Z"
        b_nonce = sha1(str(random.random()).encode()).digest()
        b_digest = sha1(b_nonce + created.encode() + api_key.encode()).digest()
        c = 'UsernameToken Username="{0}", PasswordDigest="{1}", Nonce="{2}", \
             Created="{3}"'
        return c.format(username, b64encode(b_digest).decode(),
                        b64encode(b_nonce).decode(), created)


    # Upload blog to hatena
    def create_data_blog(self, title, body, username, draft, imgdate=None):

        template = """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom" \
         xmlns:app="http://www.w3.org/2007/app">
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

        if imgdate:
             now = imgdate
             # print('specify date')
        else:
            now = datetime.now()
            # print('use now')
        dtime = now.replace(microsecond=0).isoformat()
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


    def post_hatena(self, data, headers, username, blogname):
        url = 'http://blog.hatena.ne.jp/{0}/{1}/atom/entry' \
            .format(username, blogname)
        r = requests.post(url, data=data, headers=headers)

        if r.status_code != 201:
            print('ブログ生成エラーが発生しました\n' + 'status_code: '
                  + str(r.status_code) + '\n' + 'message: ' + r.text)
        else:
            print("ブログエントリ作成しました。")


    # Upload images to hatena foto life
    def create_data_foto(self, filename):
        try:
            infile = open(filename, 'rb')
            files = infile.read()
        except IOError:
            print(filename, ":ファイルオープンに失敗しました")
            data_foto = None
        else:
            ext = Path(filename).suffix
            ext = ext[1:]
            if ext == "jpg":
                ext = "jpeg"
            uploadData = b64encode(files)
            template = """
        <entry xmlns="http://purl.org/atom/ns#">
        <title>{0}</title>
        <content mode="base64" type="image/{1}">{2}</content>
        </entry>
            """
            imgname = os.path.basename(filename)
            data_foto = template.format(imgname, ext, uploadData.decode())

        return data_foto


    def upload_foto(self, data, headers):
        url = 'http://f.hatena.ne.jp/atom/post/'
        r = requests.post(url, data=data, headers=headers)
        uploaded = False
        fotolink = None

        if r.status_code != 201:
            print('画像のアップロードに失敗しました\n' + 'status_code: '
                  + str(r.status_code) + '\n' + 'message: ' + r.text)
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


    def read_config(self):
        apikey=base_directory_r=username=blogname=draft=None
        config = configparser.ConfigParser()
        if (not os.path.exists('hatenaposterConfig.txt')):
            print('コンフィグファイル"hatenaposterConfig.txt"が見つかりません')
        else:
            try:
                config.read(os.path.expanduser('hatenaposterConfig.txt'), 'UTF-8')
                apikey = config.get('base', 'api_key')
                base_directory = config.get('base', 'base_directory')
                username = config.get('base', 'username')
                blogname = config.get('base', 'blogname')
                draft = config.get('base', 'draft')
                # Windowsパスで\が用いられている場合、\\に変換
                base_directory_r = repr(base_directory).replace("'", "")

                if (not os.path.exists(base_directory)):
                    print("画像ディレクトリの指定が間違っています")

            except configparser.NoSectionError:
                print("[base]セクションが見つかりません。")
            except configparser.NoOptionError:
                print("設定ファイルの設定項目に誤りがあります。")
            
        return apikey, base_directory_r, username, blogname, draft

    def check_config(self):
        valid = False
        apikey, base_directory, username, blogname, draft = self.read_config()
        if apikey and \
        os.path.exists(base_directory) and \
        username and \
        blogname and \
        (draft == 'yes' or draft == 'no'):
            valid = True
        return valid

    def write_config(self, apikey, base_directory, username, blogname, draft):
        config = configparser.ConfigParser()
        config['base'] = {}
        config['base']['api_key'] = apikey
        config['base']['base_directory'] = base_directory
        config['base']['username'] = username
        config['base']['blogname'] = blogname
        config['base']['draft'] = draft
        with open('hatenaposterConfig.txt', 'w') as configfile:
            config.write(configfile)

    def sendall(self):
        dateset = set()
        api_key, base_directory, username, blogname, draft = self.read_config()
        imagedates = set()
        it = os.listdir(base_directory)
        for entry in it:
            rootname, ext = os.path.splitext(entry)
            imgdate = picktimestr.picktimestr(entry)
            if ext in {'.jpg', '.jpeg', '.png', '.bmp'} and imgdate:
                imagedates.add(imgdate)
        sortedlist = list(imagedates)
        sortedlist.sort()

        for i, imgdate in enumerate(sortedlist):
            self.hatenaposter(date=imgdate)
            print('ブログ送信済み件数 (', i+1, '/', len(sortedlist), ')')

    def hatenaposter(self, filename=None, date=None):
        api_key, base_directory, username, blogname, draft = self.read_config()
        headers = {'X-WSSE': self.wsse(username, api_key)}
        # ファイル指定送信
        if filename is not None:
            imgfilenames = (filename,)
            imgdate = picktimestr.picktimestr(filename)
            targetday = imgdate if imgdate is not None else (datetime.today() + timedelta(days=-1))
        # 日付指定送信 or 昨日分送信
        else:
            if date is not None:
                targetday = date
            else:
                targetday = datetime.today() + timedelta(days=-1)
            imgfilenames = []
            filenames = glob.glob(base_directory + "/*" + targetday.strftime("%y%m%d") + "*")
            pattern = re.compile("jpg|jpeg|gif|png|bmp")
            for filename in filenames:
                if pattern.search(filename):
                    imgfilenames.append(filename)
        fotolinks = ""
        for i, filename in enumerate(imgfilenames, 1):
            print("送信開始：", filename) 
            data_foto = self.create_data_foto(filename)
            fotolink = self.upload_foto(data_foto, headers)
            if (fotolink is not None):
                print("画像送信済み (", i, "/", len(imgfilenames), ")")
                fotolinks += (fotolink + "\n")
            else:
                print(filename, " ：エラー (", i, "/", len(imgfilenames), ")")
        if (fotolinks == ""):
            print("送信対象の画像がありません.")
        else:
            body = fotolinks
            title = targetday.strftime('%Y-%m-%d')
            data_blog = self.create_data_blog(title, body, username, draft, targetday)
            self.post_hatena(data_blog, headers, username, blogname)
        print('完了しました')

if __name__ == '__main__':
    def main():
        Hatenaposter.hatenaposter()

