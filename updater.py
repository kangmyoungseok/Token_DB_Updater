#기존에 DB에 있던 토큰 이후에 더 생성된 토큰들의 정보를 DB에 저장하는 코드
import pymysql
import pandas as pd
from lib.Thegraph import *
from lib.FeatureLib import *
from decimal import Decimal

#1. 기존 파일에 존재하는 가장 최신 토큰이후에 생긴 토큰 DB에 추가
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info order by created_at_timestamp desc limit 0,1"
cursor.execute(sql)
datas = cursor.fetchall()
last_timestamp = datas[0]['created_at_timestamp']

query = query_latest % str(last_timestamp)
result = run_query(query)
switch_token(result)
datas = pd.json_normalize(result['data']['pairs']).to_dict('records')

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
token00_creator, token00_decimals, reserve_ETH, tx_count, created_at_timestamp, is_change, is_scam) 
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''


for data in datas:
    try:
        id = data['id']
        token0_name = data['token0.name']
        token1_name = data['token1.name']
        token00_id = data['token00.id']
        token00_name = data['token00.name']
        token00_symbol = data['token00.symbol']
        token00_creator = get_creatorAddress(id,token00_id)
        token00_decimals = data['token00.decimals']
        reserveETH = data['reserveETH']
        txCount = data['txCount']
        createdAtTimestamp = data['createdAtTimestamp']
        isChange = False
        isScam = False

        data['token00_creator'] = token00_creator
        cursor.execute(sql,(id,token0_name,token1_name,token00_id,token00_name,token00_symbol,token00_creator,token00_decimals,reserveETH,txCount,createdAtTimestamp,isChange,isScam)) 
    except Exception as e:
        print(e)
        
conn.commit()
conn.close()

#2. 새로 추가된 토큰들에 대해서 Feature 구함
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
INSERT INTO ai_feature(token_id, pair_id, mint_count, swap_count, burn_count, active_period, 
mint_mean_period, swap_mean_period, burn_mean_period, swap_in, swap_out, lp_lock_ratio, lp_avg, lp_std, 
lp_creator_holding_ratio, burn_ratio, token_creator_holding_ratio, created_at_timestamp, number_of_token_creation_of_creator ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''
sql2 = ''' select count(*) from pair_info where token00_creator = %s'''


for data in datas:
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
        number_of_token_creation_of_creator = cursor.fetchone()[0] + 1
               
        cursor.execute(sql,(token_id,pair_id,mint_count,swap_count,burn_count,active_period,mint_mean_period,swap_mean_period,burn_mean_period,swap_in,swap_out,lp_lock_ratio,lp_avg,lp_std,lp_creator_holding_ratio,burn_ratio,token_creator_holding_ratio,created_at_timestamp,number_of_token_creation_of_creator))
    except Exception as e:
        print(e)
        
conn.commit()
conn.close()
## 여기까지가 그냥 새로운 애들 추가해서 넣는 거고, 아래부터는 이제 1시간마다 업데이트 하는 코드 로직을 짠다.
#3. DB에서 Created_at_timestmap를 기준으로 3일 이내에 생성된 데이터들을 datas에 넣는다.

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql = "select * from pair_info order by created_at_timestamp desc "
cursor.execute(sql)
datas = cursor.fetchall()

timestamp = int(datas[0]['created_at_timestamp'])
datas2 = []
for data in datas:
    if( timestamp - (int(data['created_at_timestamp'])) < 259200):
        datas2.append(data)
    else:
        break
datas = datas2
cursor.close()



#datas 에는 생긴지 3일 이내의 토큰들의 pair_info 테이블 정보가 들어있다.
#먼저 기존과 비교해서 트랜잭션이 발생한 애들만 추가로 Feature를 뽑아야 하니까 Thegraph에서 tx를 가져와야 한다.
#4. 기존 DB에 있는 데이터가 추가적인 트랜잭션이 발생했는지 검사 data['is_change']

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
UPDATE pair_info set tx_count = %s,reserve_ETH = %s where id=%s
'''

query = query_iter % datas[-1]['created_at_timestamp']
result = run_query(query)
pairs = result['data']['pairs']


tx_list = {}
for pair in pairs:
    tx_list[pair['id']] = [int(pair['txCount']) , Decimal(pair['reserveETH'])]
 

for data in datas:
    try:
        tx_count,reserveETH = tx_list[data['id']]
        if(data['tx_count'] == tx_count):
            data['is_change'] = False
        else:
            cursor.execute(sql,(tx_count,reserveETH,data['id']))
            data['is_change'] = True
    except Exception as e:
        print(e)

conn.commit()
conn.close()

#5. 변화가 발생했고(True) & 스캠이 이미 발생하지 않은(false) 토큰들은 데이터를 다시 업데이트 한다.
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()
sql = '''
UPDATE ai_feature set mint_count = %s, swap_count = %s, burn_count = %s, active_period = %s,
mint_mean_period = %s, swap_mean_period = %s, burn_mean_period=%s, swap_in = %s, swap_out = %s, lp_lock_ratio = %s
, lp_avg = %s, lp_std = %s, lp_creator_holding_ratio = %s, burn_ratio = %s, token_creator_holding_ratio = %s where 
token_id = %s
'''

for data in datas:
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

            cursor.execute(sql,(mint_count,swap_count,burn_count,active_period,mint_mean_period,swap_mean_period,burn_mean_period,swap_in,swap_out,lp_lock_ratio,lp_avg,lp_std,lp_creator_holding_ratio,burn_ratio,token_creator_holding_ratio,token_id))
        except Exception as e:
            print(e)       

conn.commit()
conn.close()
