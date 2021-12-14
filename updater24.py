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
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

#1. 기존 파일에 존재하는 가장 최신 토큰이후에 생긴 토큰 DB에 추가
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info order by created_at_timestamp desc limit 0,1"
cursor.execute(sql)
datas = cursor.fetchall()
last_timestamp = datas[0]['created_at_timestamp']

query = query_latest % str(last_timestamp)
result = run_query(query)
pair_frame = []
switch_token(result)
for pair in result['data']['pairs']:
    if((pair['token0']['symbol'] != 'WETH') and (pair['token1']['symbol'] !='WETH' )):
      continue
    pair_frame.append(pair)

datas = pd.json_normalize(pair_frame).to_dict('records')

if(len(datas) == 1000):
    last_timestamp = datas[-1]['createdAtTimestamp']
    query = query_latest % str(last_timestamp)
    result = run_query(query)
    switch_token(result)
    datas2 = pd.json_normalize(result['data']['pairs']).to_dict('records')
    datas.extend(datas2)
    if(len(datas2) == 1000 ):
        last_timestamp = datas2[-1]['createdAtTimestamp']
        query = query_latest % str(last_timestamp)
        result = run_query(query)
        switch_token(result)
        datas3 = pd.json_normalize(result['data']['pairs']).to_dict('records')
        datas.extend(datas3)


sql = '''
INSERT INTO pair_info(id, token0_name,token1_name, token00_id, token00_name, token00_symbol, 
token00_creator, token00_decimals, reserve_ETH, tx_count, created_at_timestamp, is_change, is_scam, verified, contract_group, similarity ) 
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''


sql2 = 'select * from contract_group'
cursor.execute(sql2)
contract_groups =  cursor.fetchall()
group_list = {}
group_list['0x0000'] = 0
for contract in contract_groups:
    group_list[contract['contract_address']] = contract['group_id']


file_list = os.listdir('/home/ec2-user/Token_DB_Updater/scam_contract/')
scam_contracts = []
for file in  file_list:
  file = '/home/ec2-user/Token_DB_Updater/scam_contract/' + file
  with open(file, 'r', encoding='utf-8-sig', newline='') as input_file :
      groupcode = input_file.read()
      scam_contracts.append({'address' : file[-46:-4] ,'groupcode' : groupcode})
      

for data in tqdm(datas,desc="adding new tokens :"):
    try:
        id = data['id']
        token0_name = data['token0.name']
        token1_name = data['token1.name']
        token00_id = data['token00.id']
        token00_name = data['token00.name']
        token00_symbol = data['token00.symbol']
        token00_creator = get_creatorAddress(id,token00_id)
        token00_decimals = data['token00.decimals']
        reserveETH = float(data['reserveETH']) / 2
        txCount = data['txCount']
        createdAtTimestamp = data['createdAtTimestamp']
        isChange = False
        isScam = False
        verified,address,similarity = check_similarity(scam_contracts,token00_id)
        contract_group = group_list[address]
        data['token00_creator'] = token00_creator
        cursor.execute(sql,(id,token0_name,token1_name,token00_id,token00_name,token00_symbol,token00_creator,token00_decimals,reserveETH,txCount,createdAtTimestamp,isChange,isScam,verified,contract_group,similarity))
        conn.commit() 
    except Exception as e:
        print("error in adding new tokens")
        print(e)
        
conn.commit()
conn.close()

#2. 새로 추가된 토큰들에 대해서 Feature 구함
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
INSERT INTO ai_feature(token_id, pair_id, mint_count, swap_count, burn_count, active_period, 
mint_mean_period, swap_mean_period, burn_mean_period, swap_in, swap_out, lp_lock_ratio, lp_avg, lp_std, 
lp_creator_holding_ratio, burn_ratio, token_creator_holding_ratio, created_at_timestamp, number_of_token_creation_of_creator,unlock_date ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''
sql2 = ''' select count(*) from pair_info where token00_creator = %s'''


for data in tqdm(datas,desc="get features: "):
    try:
        token_id = data['token00.id']
        pair_id = data['id']
        # Feature Part 1
        holders = get_holders(data['id'])
        lp_lock_ratio = get_Lock_ratio(holders)
        lp_avg, lp_std = calc_LP_distribution(holders)
        lp_creator_holding_ratio = get_Creator_ratio(holders,data['token00_creator'])
        
        # Feature Part 2
        pair_address = data['id']
        mint_data_transaction = call_theGraph_mint(pair_address)
        swap_data_transaction = call_theGraph_swap(pair_address)
        burn_data_transaction = call_theGraph_burn(pair_address)

        mint_count = len(mint_data_transaction)
        swap_count = len(swap_data_transaction)
        burn_count = len(burn_data_transaction)
        
        initial_timestamp = int(mint_data_transaction[0]['timestamp'])
        last_timestamp = get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction)
        active_period = last_timestamp - initial_timestamp
        mint_mean_period = int(get_mint_mean_period(mint_data_transaction,initial_timestamp))
        swap_mean_period = int(get_swap_mean_period(swap_data_transaction,initial_timestamp))
        burn_mean_period = int(get_burn_mean_period(burn_data_transaction,initial_timestamp))

        swap_in,swap_out = swap_IO_rate(swap_data_transaction,token_index(data))
        
        # Feature part 3
        token_holders = get_holders(data['token00.id'])   
        burn_ratio = get_burn_ratio(token_holders)
        token_creator_holding_ratio = get_creator_ratio(token_holders,data['token00_creator'])
        
        created_at_timestamp = data['createdAtTimestamp']
        cursor.execute(sql2,data['token00_creator'])
        number_of_token_creation_of_creator = cursor.fetchone()[0] 

                # Feature part 4 -> unlock_date 구하기
        if(lp_lock_ratio > 0):
            unlock_date = get_unlock_date(holders,data['token00_creator'])
        else:
            unlock_date = 0
        
        cursor.execute(sql,(token_id,pair_id,mint_count,swap_count,burn_count,active_period,mint_mean_period,swap_mean_period,burn_mean_period,swap_in,swap_out,lp_lock_ratio,lp_avg,lp_std,lp_creator_holding_ratio,burn_ratio,token_creator_holding_ratio,created_at_timestamp,number_of_token_creation_of_creator,unlock_date))
        conn.commit()
    except Exception as e:
        print("error in get features")
        print(e)
        
conn.commit()
conn.close()


### 3. 업데이트 전에 추가된 토큰을 포함해서 90일 이내의 토큰들의 스캠 탐지를 먼저 수행
pairs = []
current_time = int(time.time())
limit_time = current_time
while(1):
    query = query_scam_iter % limit_time
    result = run_query(query) 
    pairs.extend(result['data']['pairs'])
    limit_time = int(result['data']['pairs'][999]['createdAtTimestamp'])
    if( (current_time - limit_time) > 12960000):
      break



conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info where created_at_timestamp > %s" %limit_time
cursor.execute(sql)
datas = cursor.fetchall()
conn.close()

sus_list = {}

for pair in pairs:
  sus_list[pair['id']] = float(pair['reserveETH']) / 2

#스캠 검사 이후 DB에 입력
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()

sql = '''
INSERT INTO scam_token(token_id,pair_id,tx_id,rugpull_timestamp,before_ETH,after_ETH) VALUES(%s,%s,%s,%s,%s,%s)
'''
sql2 = '''
UPDATE pair_info set is_scam=true where token00_id = %s
'''


for data in tqdm(datas,desc="rugpull check: ") :
  if( (data['is_scam'] == 1) or (data['tx_count'] < 3)  )  :
    continue
  try:
    before_ETH = Decimal(data['reserve_ETH'])
    current_ETH = Decimal(sus_list[data['id']])
    if(current_ETH > 0.1):
        continue
    is_rugpull_occur(data)
    if(data['is_scam'] == True):  #DB에 데이터 넣기
        token_id = data['token_id']
        pair_id = data['id']
        tx_id = data['tx_id']
        rugpull_timestamp = data['rugpull_timestamp']
        before_ETH = data['before_ETH']
        after_ETH = data['after_ETH']
        print("러그풀 발생 before : %d , after : %d",before_ETH,current_ETH)
        cursor.execute(sql2,token_id)
        cursor.execute(sql,(token_id,pair_id,tx_id,rugpull_timestamp,before_ETH,after_ETH))
        conn.commit()
    else:
        continue
      

  except Exception as e:
    print("error in rugpull check")
    print(e)
    continue

conn.commit()


## 러그풀 발생했는지에 대한 검증 이후, 발생하지 않은 토큰들에 대해서 Feature 업데이트.
#4. DB에서 Created_at_timestmap를 기준으로 60일 이내에 생성된 데이터들을 datas에 넣는다.

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
timestamp = limit_time
sql = "select * from ai_feature join pair_info on pair_info.id = ai_feature.pair_id where pair_info.created_at_timestamp > %s order by pair_info.created_at_timestamp desc  "
cursor.execute(sql,timestamp)
datas = cursor.fetchall()
cursor.close()

#datas 에는 생긴지 90일 이내의 토큰들의 pair_info 테이블 정보가 들어있다.
#먼저 기존과 비교해서 트랜잭션이 발생한 애들만 추가로 Feature를 뽑아야 하니까 Thegraph에서 tx를 가져와야 한다.
#5. 기존 DB에 있는 데이터가 추가적인 트랜잭션이 발생했는지 검사 data['is_change']

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
UPDATE pair_info set tx_count = %s,reserve_ETH = %s where id=%s
'''

current_time = int(time.time())
limit_time = current_time
pairs = []
while(1):
    query = query_scam_iter % limit_time
    result = run_query(query) 
    pairs.extend(result['data']['pairs'])
    limit_time = int(result['data']['pairs'][999]['createdAtTimestamp'])
    if( (current_time - limit_time) > 12960000):
      break



tx_list = {}
for pair in pairs:
    tx_list[pair['id']] = [int(pair['txCount']) , Decimal(pair['reserveETH']) / 2 ]
 

for data in datas:
    try:
        tx_count,reserveETH = tx_list[data['id']]
        if(data['tx_count'] == tx_count):
            data['is_change'] = False
        else:
            cursor.execute(sql,(tx_count,reserveETH,data['id']))
            data['is_change'] = True
    except Exception as e:
        print("error in check is_change")
        print(e)

conn.commit()
conn.close()


#5. 변화가 발생했고(True) & 스캠이 이미 발생하지 않은(false) 토큰들은 데이터를 다시 업데이트 한다.
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
UPDATE ai_feature set mint_count = %s, swap_count = %s, burn_count = %s, active_period = %s,
mint_mean_period = %s, swap_mean_period = %s, burn_mean_period=%s, swap_in = %s, swap_out = %s, lp_lock_ratio = %s
, lp_avg = %s, lp_std = %s, lp_creator_holding_ratio = %s, burn_ratio = %s, token_creator_holding_ratio = %s, unlock_date = %s where 
token_id = %s
'''

for data in tqdm(datas,desc="update token feature: "):
    if( (data['is_change'] == True )and (data['is_scam'] == False) ):
        try:
            data['token0.name'] = data['token0_name']
            token_id = data['token00_id']
            pair_id = data['id']
            # Feature Part 1
            holders = get_holders(data['id'])
            lp_lock_ratio = get_Lock_ratio(holders)
            lp_avg, lp_std = calc_LP_distribution(holders)
            lp_creator_holding_ratio = get_Creator_ratio(holders,data['token00_creator'])
            
            # Feature Part 2
            pair_address = data['id']
            mint_data_transaction = call_theGraph_mint(pair_address)
            swap_data_transaction = call_theGraph_swap(pair_address)
            burn_data_transaction = call_theGraph_burn(pair_address)

            mint_count = len(mint_data_transaction)
            swap_count = len(swap_data_transaction)
            burn_count = len(burn_data_transaction)

            initial_timestamp = int(mint_data_transaction[0]['timestamp'])
            last_timestamp = get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction)
            active_period = last_timestamp - initial_timestamp
            mint_mean_period = int(get_mint_mean_period(mint_data_transaction,initial_timestamp))
            swap_mean_period = int(get_swap_mean_period(swap_data_transaction,initial_timestamp))
            burn_mean_period = int(get_burn_mean_period(burn_data_transaction,initial_timestamp))

            swap_in,swap_out = swap_IO_rate(swap_data_transaction,token_index(data))

            # Feature part 3
            token_holders = get_holders(data['token00_id'])   
            burn_ratio = get_burn_ratio(token_holders)
            token_creator_holding_ratio = get_creator_ratio(token_holders,data['token00_creator'])
            # Feature part 4 -> Unlock Time
            if( (lp_lock_ratio >0 )  and ( (data['unlock_date'] == 0) or (data['unlock_date'] == None) ) ):
                unlock_date = get_unlock_date(holders,data['token00_creator'])
            else:
                try:
                    unlock_date = data['unlock_date']
                except:
                    unlock_date = 0

            cursor.execute(sql,(mint_count,swap_count,burn_count,active_period,mint_mean_period,swap_mean_period,burn_mean_period,swap_in,swap_out,lp_lock_ratio,lp_avg,lp_std,lp_creator_holding_ratio,burn_ratio,token_creator_holding_ratio,unlock_date,token_id))
            conn.commit()
        except Exception as e:
            print("erorr in update feature")
            print(e)      

conn.commit()
conn.close()


#6. Feature들의 업데이트 이후, 업데이트된 Feature들로 AI 모델에 넣어야 한다.
# 스캠이 발생한 토큰[is_scam == true]은 ai 모델에 넣지 않는다.
# datas에 있는 토큰들에 대해서 진행
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)
timestamp = limit_time
sql = "select * from ai_feature join pair_info on ai_feature.pair_id = pair_info.id where pair_info.created_at_timestamp > %d " %timestamp
sql2 = "update ai_feature set unlock_date = %s where token_id =%s"
cursor.execute(sql)
datas = cursor.fetchall()
current_time = int(time.time())

for data in datas:
    if(data['unlock_date'] == None):
        data['unlock_date'] = 0


unlock_list = []
result = []
for data in datas:
    if(data['is_scam'] == 1):
        continue
    dataset = {}
    try:
        if(int(data['lp_lock_ratio']) > 0):
            # unlock_date가 3일 이내면 lock_ratio를 0으로 간주하여 탐지
            if( data['unlock_date'] - current_time  < 300000 ):
                # unlock_date가 하루 미만 남았으면 relock 가능성을 고려하여, unlock타임을 다시 가져온다.
                if( abs(data['unlock_date'] - current_time) < 86400):
                    holders = get_holders(data['id'])
                    unlock_date = get_unlock_date(holders,data['token00_creator'])
                    if(int(data['unlock_date']) != int(unlock_date)):
                        cursor.execute(sql2,(unlock_date,data['token_id']))
                # unlock_date가 끝난 직후에 러그풀 치는 애들이 많음. unlock date가 끝나기 전 3일 끝난 직후 1주일이 가장 위험하다고 간주.
                if ( abs(data['unlock_date'] - current_time) < 604800):
                    print('pair[%s] : unlock after %s hour' %(data['pair_id'], (data['unlock_date'] - current_time)/3600  ))
                    unlock_list.append(data['pair_id'])
                data['lp_lock_ratio'] = 0
            
        dataset['token_id'] = data['token_id']
        dataset['reserve_ETH'] = data['reserve_ETH']
        dataset['id'] = data['pair_id'] 
        dataset['mint_count_per_week'] = data['mint_count'] / ((int(data['active_period']) / (60* 60 * 24 * 7)) + 1)
        dataset['burn_count_per_week'] =data['burn_count'] / ((int(data['active_period']) / (60* 60 * 24 * 7)) + 1)
        tx_count = data['mint_count'] + data['burn_count'] + data['swap_count']
        dataset['mint_ratio'] = data['mint_count'] / tx_count
        dataset['swap_ratio'] = data['swap_count'] / tx_count
        dataset['burn_ratio'] = data['burn_count'] / tx_count
        dataset['mint_mean_period'] = data['mint_mean_period'] / data['active_period']
        dataset['swap_mean_period'] = data['swap_mean_period'] / data['active_period']
        dataset['burn_mean_period'] = data['burn_mean_period'] / data['active_period']
        dataset['swap_in_per_week'] = data['swap_in'] /((int(data['active_period']) / (60* 60 * 24 * 7)) + 1)
        dataset['swap_out_per_week'] = data['swap_out'] / ((int(data['active_period']) / (60* 60 * 24 * 7)) + 1)
        dataset['swap_rate'] = data['swap_in'] / (data['swap_out'] + 1)
        dataset['lp_avg'] = data['lp_avg'] 
        dataset['lp_std'] = data['lp_std']
        dataset['lp_creator_holding_ratio'] = data['lp_creator_holding_ratio']
        dataset['lp_lock_ratio'] = data['lp_lock_ratio']
        dataset['token_burn_ratio'] = data['burn_ratio']
        dataset['token_creator_holding_ratio'] = data['token_creator_holding_ratio']
        dataset['number_of_token_creation_of_creator'] = data['number_of_token_creation_of_creator']
    except Exception as e:
        print("error in convert ai_feature to dataset ")
        print(e)
        continue
    result.append(dataset)



# 7. 결과로 나온 Dataset을 통해서 AI 모델의 점수 계산
# 7. 결과로 나온 Dataset을 통해서 AI 모델의 점수 계산
dataset = pd.DataFrame(result)
origin = dataset
dataset = dataset.drop(columns = ['id','reserve_ETH','token_id'])
dataset = dataset.dropna(how='any',axis = 0)

scaler = MinMaxScaler()
dataset[ : ] = scaler.fit_transform(dataset[ : ])

model = keras.models.load_model('/home/ec2-user/Token_DB_Updater/ann97.h5')
model.summary()

result = model.predict(dataset)
origin['predict'] = result



datas = origin.to_dict('records')
for data in datas:
    data['predict'] = int(data['predict'] * 100)

filename = '/home/ec2-user/Token_DB_Updater/ai_feature/Dataset[24]_'+datetime.datetime.now().strftime('%m.%d_%H')+'.csv'
pd.DataFrame(datas).to_csv(filename,encoding='utf-8-sig',index=False)

# 8. AI 모델 점수 낸거 추가.
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select idx from graph_table where pair_id = %s"
sql2 = "UPDATE graph_table set idx = {}, {} = {}, {} = {}, current_score = {} where pair_id = '{}'" 
sql3 = "insert into graph_table (token_id,pair_id,idx,is_latest,ai0,eth0,current_score) values (%s,%s,0,1,%s,%s,%s)"

for data in tqdm(datas,desc="input graph_table"):    
    try:
        cursor.execute(sql,data['id'])
        result = cursor.fetchone()
        idx = result['idx'] + 1
        #idx가 존재하면 기존에 있던 데이터에서 업데이트 수행
        ai_idx = 'ai{}'.format(idx) 
        eth_idx = 'eth{}'.format(idx)
        if(data['id'] in unlock_list):
            ai_score = 99
        else:
            ai_score = data['predict']
        eth_amount = data['reserve_ETH']
        current_score = ai_score
        sql4 = sql2.format(idx,ai_idx,ai_score,eth_idx,eth_amount,current_score,data['id'])
        cursor.execute(sql4)
    except:
        #idx가 존재하지 않으면, 새로운 행 추가
        token_id = data['token_id']
        pair_id = data['id']
        if(data['id'] in unlock_list):
            ai0 = 99
        else:
            ai0 = data['predict']
        eth0 = data['reserve_ETH']
        cursor.execute(sql3,(token_id, pair_id, ai0, eth0,ai0))
    conn.commit()
conn.close()

# 9. 3일 이내의 토큰 중, 3일 이후로 넘어간 토큰들 is_latest 수정
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)
timestamp = int(time.time()) - 200000
sql = "select * from pair_info join graph_table on pair_info.id = graph_table.pair_id where pair_info.created_at_timestamp < 1638992511 and is_scam = 0 and graph_table.is_latest = 1"
sql9 = "delete from graph_table where pair_id = '{}'"
sql2 = "INSERT INTO graph_table(token_id,pair_id,idx,is_latest,ai0,ai1,ai2,eth0,eth1,eth2,current_score) values ('{}','{}',{},{},{},{},{},{},{},{},{})"
sql1 = "INSERT INTO graph_table(token_id,pair_id,idx,is_latest,ai0,ai1,eth0,eth1,current_score) values ('{}','{}',{},{},{},{},{},{},{})"
sql0 = "INSERT INTO graph_table(token_id,pair_id,idx,is_latest,ai0,eth0,current_score) values ('{}','{}',{},{},{},{},{})"


cursor.execute(sql,timestamp)
datas = cursor.fetchall()

for data in datas:
    token_id = data['token_id']
    pair_id = data['pair_id']    
    idx = data['idx']
    is_latest = 0
    idx_remain = idx % 8 
    idx = int(idx/8)
    if(idx == 2):
        ai0_idx = 'ai' + str(idx_remain)
        ai1_idx = 'ai' + str(idx_remain + 8)
        ai2_idx = 'ai' + str(idx_remain + 16)
        eth0_idx = 'eth' + str(idx_remain)
        eth1_idx = 'eth' + str(idx_remain + 8)
        eth2_idx = 'eth' + str(idx_remain + 16)
        ai0, ai1, ai2 = data[ai0_idx], data[ai1_idx], data[ai2_idx]
        eth0, eth1, eth2 = data[eth0_idx], data[eth1_idx], data[eth2_idx] 
        current_score = ai2
        sql = sql9.format(pair_id)
        cursor.execute(sql)
        sql = sql2.format(token_id,pair_id,idx,is_latest,ai0,ai1,ai2,eth0,eth1,eth2,current_score)
        cursor.execute(sql)
    if(idx == 1):
        ai0_idx = 'ai' + str(idx_remain)
        ai1_idx = 'ai' + str(idx_remain + 8)
        eth0_idx = 'eth' + str(idx_remain)
        eth1_idx = 'eth' + str(idx_remain + 8)
        ai0, ai1 = data[ai0_idx], data[ai1_idx]
        eth0, eth1 = data[eth0_idx], data[eth1_idx] 
        current_score = ai1
        sql = sql9.format(pair_id)
        cursor.execute(sql)
        sql = sql1.format(token_id,pair_id,idx,is_latest,ai0,ai1,eth0,eth1,current_score)
        cursor.execute(sql)
    if(idx == 0):
        ai0_idx = 'ai' + str(idx_remain)
        eth0_idx = 'eth' + str(idx_remain)
        ai0 = data[ai0_idx]
        eth0 = data[eth0_idx] 
        current_score = ai0
        sql = sql9.format(pair_id)
        cursor.execute(sql)
        sql = sql0.format(token_id,pair_id,idx,is_latest,ai0,eth0,current_score)
        cursor.execute(sql)
    conn.commit()
    
conn.close()


#9. Warning 검증
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

# scam_address 배열에 먼저 선언
sql = "select token00_creator from pair_info where is_scam = 1"
cursor.execute(sql)
datas = cursor.fetchall()

scam_address = []
for data in datas:
    scam_address.append(data['token00_creator'])

# 정상인 토큰들 DB에서 불러오기
sql3 = "select * from pair_info join ai_feature on pair_info.id = ai_feature.pair_id where is_scam = 0"
cursor.execute(sql3)
datas = cursor.fetchall()

# 모든 정상 토큰들에 대해서 Warning 라벨링 하기
for data in datas:
    try:
        data['warning'] = 0
        if(data['similarity'] == None):
            data['similarity'] = 0
        if(data['similarity'] > 0.9):
            data['warning'] = 3
        
        swap_rate = data['swap_in'] / (data['swap_out'] + 1)
        if(swap_rate > 15):
            data['warning'] = 2

        if(data['token00_creator'] in scam_address):
            data['warning'] = 1
    except Exception as e:
        print("error in warning")
        print(e)

sql4 = "update pair_info set warning = %s where id = %s"
for data in datas:
    cursor.execute(sql4,(data['warning'],data['id']))
    conn.commit()


sql5 = "select * from pair_info join graph_table on pair_info.id = graph_table.pair_id where is_scam = 0 and current_score > 98 and warning = 0"
cursor.execute(sql5)
datas = cursor.fetchall()

for data in datas:
    cursor.execute(sql4,(4,data['id']))
    conn.commit()
