#기존에 DB에 있던 토큰 이후에 더 생성된 토큰들의 정보를 DB에 저장하는 코드
import pymysql
import pandas as pd
from lib.Thegraph import *
from lib.FeatureLib import *
from decimal import Decimal
import time
from tqdm import tqdm
import datetime
from tensorflow import keras
import pandas as pd
import os

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql1 = 'select * from contract_group'
cursor.execute(sql1)
contract_groups =  cursor.fetchall()
group_list = {}
group_list['0x0000'] = 0
for contract in contract_groups:
    group_list[contract['contract_address']] = contract['group_id']

# Scam_contracts들 먼저 배열에 정의
file_list = os.listdir('/home/ec2-user/Token_DB_Updater/scam_contract/')
scam_contracts = []
for file in  file_list:
  file = '/home/ec2-user/Token_DB_Updater/scam_contract/' + file
  with open(file, 'r', encoding='utf-8-sig', newline='') as input_file :
      groupcode = input_file.read()
      scam_contracts.append({'address' : file[-46:-4] ,'groupcode' : groupcode})
      
# 전체 데이터 불러오기
sql2 = "select * from pair_info where is_scam = 0 and verified is null order by created_at_timestamp desc "
cursor.execute(sql2)
datas = cursor.fetchall()

# 반복문 돌면셔 업데이트
sql3 = "UPDATE pair_info set verified = %s, contract_group = %s, similarity = %s where token00_id = %s"
for data in tqdm(datas,desc="get similarity"):
    try:
        token00_id = data['token00_id']
        verified,address,similarity = check_similarity(scam_contracts,token00_id)
        print(similarity)
        contract_group = group_list[address]    #그룹 아이디로 넣을 것.
        cursor.execute(sql3,(verified,contract_group,similarity,token00_id))
        conn.commit()
    except KeyboardInterrupt:
        print("stop it")
        break
    except Exception as e:
        print("error in get similarity")
        print(e)

