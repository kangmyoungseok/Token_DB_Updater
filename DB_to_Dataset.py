import pymysql
import time
import pandas as pd
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)

current_time = int(time.time())

three_day = 60 * 60 * 24 * 3 
three_days_ago_timestamp = current_time - three_day

sql = "select * from ai_feature where created_at_timestamp > %d" %three_days_ago_timestamp
cursor.execute(sql)
datas = cursor.fetchall()

result = []
for data in datas:
    dataset = {}
    try:
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
        print(e)
        print([tx_count,data['swap_count'],data['active_period']])
        continue
    result.append(dataset)

pd.DataFrame(result).to_csv('./ai_feature/Dataset_v1.0.csv',encoding='utf-8-sig',index=False)
    
    
