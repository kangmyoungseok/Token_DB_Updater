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
import numpy as np
from sklearn.preprocessing import MinMaxScaler
datas = pd.read_csv('./ai_feature/Dataset_12.01_17.csv',encoding = 'utf-8-sig').to_dict('records')


# 8. AI 모델 점수 낸거 추가.
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select idx from graph_table where pair_id = %s"
sql2 = "UPDATE graph_table set idx = {}, {} = {}, {} = {} where pair_id = '{}'" 
sql3 = "insert into graph_table (token_id,pair_id,idx,is_latest,ai0,eth0) values (%s,%s,0,0,%s,%s)"

for data in tqdm(datas,desc="input graph_table"):    
    try:
        cursor.execute(sql,data['id'])
        result = cursor.fetchone()
        idx = result['idx'] + 1
        #idx가 존재하면 기존에 있던 데이터에서 업데이트 수행
        ai_idx = 'ai{}'.format(idx)
        eth_idx = 'eth{}'.format(idx)
        ai_score = data['predict']
        eth_amount = data['reserve_ETH']
        sql4 = sql2.format(idx,ai_idx,ai_score,eth_idx,eth_amount,data['id'])
        cursor.execute(sql4)
    except:
        #idx가 존재하지 않으면, 새로운 행 추가
        token_id = data['token_id']
        pair_id = data['id']
        ai0 = data['predict']
        eth0 = data['reserve_ETH']
        cursor.execute(sql3,(token_id, pair_id, ai0, eth0))

conn.commit()