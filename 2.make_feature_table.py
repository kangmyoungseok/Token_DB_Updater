import pymysql
import pandas as pd

try:
    conn = pymysql.connect(host='localhost',user='root',password='bobai123',db = 'bobai123',charset='utf8mb4')
    cursor = conn.cursor()

    #1. table 만들기
    sql = '''CREATE TABLE ai_feature (
        token_id char(50),
        pair_id char(50),
        mint_count int,
        swap_count int,
        burn_count int,
        active_period int,
        mint_mean_period int,
        swap_mean_period int,
        burn_mean_period int,
        swap_in int,
        swap_out int,
        lp_lock_ratio double,
        lp_avg double,
        lp_std double,
        lp_creator_holding_ratio 
        burn_ratio double,
        token_creator_holding_ratio double,
        PRIMARY KEY (token_id),
        FOREIGN KEY (pair_id) REFERENCES pair_info (id)
    ) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    ''' 
    cursor.execute(sql) 
except:
    print('ai feature table already exists')

datas = pd.read_csv('Pairs_v2.6.csv',encoding='utf-8-sig').to_dict('records')
