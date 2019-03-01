# coding: UTF-8

import re
from datetime import datetime

# 6桁の数字のマッチをすべて取得し、最初に日付に変換できたものを使用
# 初回マッチでループを抜ける
# datetimeオブジェクトを返却

matchFlag = False

def picktimestr(datestr):
    dt = None
    # print('■for ', line.strip())
    # 6桁以上の最大桁数で数字マッチ
    imgdates = re.findall('(\d{6}\d*)', datestr)
    if imgdates: # 数字6桁（以上）がマッチした場合
        # print(len(imgdates) ,' matched.')
        # マッチした文字列それぞれについて検証
        for imgdate in imgdates:
            # マーカーを一文字ずつ進めて、そこからの6桁の数字でマッチング
            for i in range(0,len(imgdate)-5):
                slicedstr = imgdate[i:i+6]
                # print('in ', slicedstr)
                try:
                    dt = datetime.strptime(slicedstr, r'%y%m%d')
                except ValueError:
                    # print('digits is not date')
                    pass
                else:
                    # print('date digits', dt)
                    matchFlag = True
                    break # imgdate走査
            if matchFlag:
                break # マッチ文字列群
        # if文は勝手にぬける
    return dt

