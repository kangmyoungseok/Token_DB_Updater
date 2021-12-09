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

from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

 #수정해야하는 부분
#
mykey = 'A78Z2CZPJI82R1QCSCDX61P4HF9KQXGX8D'  #이더스캔 API키 적기
line = '0x45dac6c8776e5eb1548d3cdcf0c5f6959e410c3a'   #소스코드 가져올 토큰 컨트랙트 주소 적기
path_dir = './token_group/token_group'  #폴더 경로
#
#수정해야하는 부분

repos_url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address='+line+'&apikey='+mykey
gh_session = requests.Session()
    
tokenname = line
result = json.loads(gh_session.get(repos_url).text)
sourcecode = result["result"][0]["SourceCode"]

#소스코드 verified 여부 확인
abi = result["result"][0]['ABI']
notverified = 0
if 'Contract source code not verified' in abi :
      notverified = 1


#그룹 결과 저장되어있는 Dataframe 불러오기
final_group = pd.read_csv('./finalgroup.csv', index_col = 0)


#그룹 결과 파일과 유사도 비교
file_list = os.listdir(path_dir)

if notverified == 0 : #verified된 소스코드라면 유사도 체크함
  isEnd = False
  max_simratio = -1 #초기값세팅
  for file in file_list:
    filename = file.replace('.txt', '')
    file = path_dir + '/' + file
    with open(file, 'r', encoding='utf-8', newline='') as input_file :
      groupcode = input_file.read()
      simratio = similar(sourcecode, groupcode)
      if max_simratio < simratio :
        max_simratio = simratio
        max_group = filename
      if simratio > 0.7:
        final_group.at[final_group['token'] == filename, 'count'] = count+1
        isEnd = True
        break

  if isEnd : #유사도 70넘는게 있으면
    similarity = simratio
    sim_group = filename
    me = tokenname
    notverified = 0
  else : 
    similarity = max_simratio
    sim_group = max_group
    me = tokenname
    notverified = 0

else : #verified 안 된 경우라면
  notverified = 1
  similarity = -1
