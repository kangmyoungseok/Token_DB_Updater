import pymysql
import time
import pandas
conn = pymysql.connect(host='localhost',user='root',password='rkdaudtjr1!',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)

current_time = int(time.time())

three_day = 60 * 60 * 24 * 3
three_days_ago_timestamp = current_time - three_day

sql = "select * from ai_feature where created_at_timestamp1 > %d" %three_days_ago_timestamp
cursor.execute(sql)
datas = cursor.fetchall()

result = []

for data in datas:
    id = data['pair_id'] 
    mint_count_per_week = 
    burn_count_per_week =
    mint_ratio =
    swap_ratio = 
    burn_ratio =
    mint_mean_period = 
    swap_mean_period =
    burn_mean_period =
    swap_in_per_week = 
    swap_out_per_week =
    swap_rate =
    lp_avg = data['lp_avg'] 
    lp_std = data['lp_std']
    lp_creator_holding_ratio = data['lp_creator_holding_ratio']
    lp_lock_ratio = data['lp_lock_ratio']
    burn_ratio = data['burn_ratio']
    token_creator_holding_ratio = data['token_creator_holding_ratio']
    number_of_token_creation_of_creator = data['number_of_token_creation_of_creator']
    
    
