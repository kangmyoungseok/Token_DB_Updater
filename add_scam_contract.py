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


#그룹 결과 파일과 유사도 비교
path_dir = '/home/ec2-user/Token_DB_Updater/scam_contract/'  #폴더 경로
file_list = os.listdir(path_dir)

sql = "Insert into contract_group(group_id,contract_address) values ({},'{}')"

index = 0
for list in file_list:
    index = index + 1
    sql2 = sql.format(index,list[:-4])
    cursor.execute(sql2)
conn.commit()
