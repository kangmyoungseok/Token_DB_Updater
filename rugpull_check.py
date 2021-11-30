#러그풀이 발생했는지 체크하는 로직. 이것도 한시간 마다 하면 되자나??? feature 구할때..~
#러그풀 발생하는지 체크하는건 생긴지 3달이내의 토큰에 대해서만 할까??? 아니면 좀더? 긁는건 별로 안걸리자늠? 
#여기있는 코드는 1시간 간격에서 체크할 용도 임.!
from time import time
from lib.FeatureLib import *
from lib.Thegraph import *
import pymysql 
from decimal import Decimal
from tqdm import tqdm
current_time = int(time())

query_scam_iter = '''
{
 pairs(first: 1000, orderBy: createdAtBlockNumber, orderDirection: desc, where: {createdAtTimestamp_lt:%s}) {
   id
   reserveETH
   txCount
   createdAtTimestamp
   createdAtBlockNumber
 }
}
''' 

def is_rugpull_occur(data):
  try:
    pair_address = data['id']
    token_id = data['token00_id']
    data['token0.name'] = data['token0_name']
    mint_data_transaction = call_theGraph_mint(pair_address)
    swap_data_transaction = call_theGraph_swap(pair_address)
    burn_data_transaction = call_theGraph_burn(pair_address)
    
    rugpull_timestamp, rugpull_change, is_rugpull, before_rugpull_Eth, after_rugpull_Eth,rugpull_method,tx_id = get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,token_index(data))
    get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,token_index(data))

    if(is_rugpull == True):
        data['token_id'] = token_id
        data['tx_id'] = tx_id
        data['rugpull_timestamp'] = rugpull_timestamp
        data['before_ETH'] = before_rugpull_Eth
        data['after_ETH'] = after_rugpull_Eth
        data['is_scam'] = True
    else:
        data['is_scam'] = False
  except Exception as e:
    data['is_scam'] = False
    print(e)
  
  return data
  
    


pairs = []
limit_time = current_time

#45일 까지의 토큰들만 스캠 검사
while(1):
    query = query_scam_iter % limit_time
    result = run_query(query) 
    pairs.extend(result['data']['pairs'])
    limit_time = int(result['data']['pairs'][999]['createdAtTimestamp'])
    if( (current_time - limit_time) > 3888000):
      print(current_time - limit_time)
      break
limit_time

#현재 이더가 0.01이하인 토큰들 리스팅 [pairs]
#DB에서도 검사할 대상 토큰들 리스팅 [datas]

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info where created_at_timestamp > %s" %limit_time
cursor.execute(sql)
datas = cursor.fetchall()
conn.close()

#스캠 검사는 부하가 많이 걸려서, reserveETH가 0.01이하인 애들만 검사한다.

sus_list = {}

for pair in pairs:
  sus_list[pair['id']] = pair['reserveETH']


#스캠 검사 이후 DB에 입력
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()

sql = '''
INSERT INTO scam_token(token_id,pair_id,tx_id,rugpull_timestamp,before_ETH,after_ETH) VALUES(%s,%s,%s,%s,%s,%s)
'''
sql2 = '''
UPDATE pair_info set is_scam=true where token00_id = %s
'''


for data in tqdm(datas,desc="processing") :
  if(data['is_scam'] == 1):
    continue
  try:
    before_ETH = Decimal(data['reserve_ETH'])
    current_ETH = Decimal(sus_list[data['id']])
    
    if( (current_ETH / before_ETH) < 0.01 ): # 이 조건을 만족한다면, 러그풀이 발생했을 거라 판단하고, 러그풀 발생지점을 찾는 코드를 돌린다.
      #print("러그풀 발생 before : %d , after : %d",before_ETH,current_ETH)
      is_rugpull_occur(data)
      if(data['is_scam'] == True):  #DB에 데이터 넣기
        token_id = data['token_id']
        pair_id = data['id']
        tx_id = data['tx_id']
        rugpull_timestamp = data['rugpull_timestamp']
        before_ETH = data['before_ETH']
        after_ETH = data['after_ETH']
        cursor.execute(sql2,token_id)
        cursor.execute(sql,(token_id,pair_id,tx_id,rugpull_timestamp,before_ETH,after_ETH))
      else:
        continue
      

  except Exception as e:
    print(e)
    continue

conn.commit()