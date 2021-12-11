# EherScan API 소스코드 뽑기
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
import re # 추가
from urllib.request import urlopen
import requests
import time
import os
import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm
from difflib import SequenceMatcher

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

#1. warning을 위해서 열 추가.

sql = "alter table pair_info add column warning tinyint after is_change"
cursor.execute(sql)

#2. Scammer가 만든 다른 토큰은 Warning을 1로 한다.
#3. swap Rate 가 비정상적
#4. Similarity

sql2 = "select token00_creator from pair_info where is_scam = 1"
cursor.execute(sql2)
datas = cursor.fetchall()

scam_address = []
for data in datas:
    scam_address.append(data['token00_creator'])

sql3 = "select * from pair_info join ai_feature on pair_info.id = ai_feature.pair_id where is_scam = 0"
cursor.execute(sql3)
datas = cursor.fetchall()

for data in datas:
    data['warning'] = 0
    if(data['similarity'] == None):
        data['similarity'] = 0
    if(data['similarity'] > 0.9):
        data['warning'] = 3
    
    swap_rate = data['swap_in'] / (data['swap_out'] + 1)
    if(swap_rate > 10):
        data['warning'] = 2

    if(data['token00_creator'] in scam_address):
        data['warning'] = 1


sql4 = "update pair_info set warning = %s where id = %s"
for data in datas:
    cursor.execute(sql4,(data['warning'],data['id']))
conn.commit()
    