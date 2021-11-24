#기존에 DB에 있던 토큰 이후에 더 생성된 토큰들의 정보를 DB에 저장하는 코드

import pymysql
import pandas as pd
from lib.Thegraph import *
from lib.FeatureLib import *

#지금은 DB가 없으니까 파일에서 읽는걸 DB에서 읽은거로 치자.
# DB에서 읽어도 Datas에 다 담아서 호환성 유지할 것

datas = pd.read_csv('./files/Pairs_v2.5.csv',encoding='utf-8-sig').to_dict('records')


#기존 파일에 존재하는 가장 최신 토큰이후에 생긴 토큰들 불러오기
last_timestamp = datas[0]['createdAtTimestamp']
# DB가 있다면 아래와 같이 초기화 할 것
# sql = "select CreatedAtTimestamp from pair_info order by createdAtTimestamp desc limit 0,1"
# cursor.execute(sql)
# result = cursor.fetchall()
# last_timestamp = result[0][0]


query = query_latest % str(last_timestamp)
result = run_query(query)
switch_token(result)
datas = pd.json_normalize(result['data']['pairs']).to_dict('records')
#datas = datas[0:10]
#len(datas)
datas[0]
# 토큰의 메인 정보가 저장되는 DB(Pair_Info Table)에 해당 데이터 저장
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
        data['error'] = ''

        data['creator_address'] = token00_creator

        # cursor.execute(sql,(id,token0_name,token1_name,token00_id,token00_name,token00_symbol,token00_creator,token00_decimals,reserveETH,txCount,createdAtTimestamp,isChange,isScam))
    except Exception as e:
        data['error'] = e
        print(e)



datas[0]
#AI에 들어갈 Feature들 구해오는 코드
#Feature 구할때 오류나면 한 번 더 호출하자.
error_list = []

for data in datas:
    try:
        # Feature Part 1
        holders = get_holders(data['id'])
        Lock_ratio = get_Lock_ratio(holders)
        LP_avg, LP_stdev = calc_LP_distribution(holders)
        LP_Creator_ratio = get_Creator_ratio(holders,data['creator_address'])
        data['holders'] = holders
        data['Lock_ratio'] = Lock_ratio
        data['LP_avg'] = LP_avg
        data['LP_stdev'] = LP_stdev
        data['LP_Creator_ratio'] = LP_Creator_ratio
        
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

        swapIn,swapOut = swap_IO_rate(swap_data_transaction,token_index(data))

        data['mint_count'] = mint_count
        data['swap_count'] = swap_count
        data['burn_count'] = burn_count
        
        data['active_period'] = active_period
        data['mint_mean_period'] = mint_mean_period
        data['swap_mean_period'] = swap_mean_period
        data['burn_mean_period'] = burn_mean_period

        data['swapIn'] = swapIn
        data['swapOut'] = swapOut

        # Feature part 3
        token_holders = get_holders(data['token00.id'])   
        burn_ratio = get_burn_ratio(token_holders)
        creator_ratio = get_creator_ratio(token_holders,data['creator_address'])

        data['token_holders'] = token_holders
        data['burn_ratio'] = burn_ratio
        data['creator_ratio'] = creator_ratio

    except Exception as e:
        print(e)
        data['error'] = e

