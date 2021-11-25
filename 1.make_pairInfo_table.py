import pymysql 
import pandas as pd

<<<<<<< HEAD
conn = pymysql.connect(host='localhost', user='root', password='rkdaudtjr1!', charset='utf8mb4') 
=======
conn = pymysql.connect(host='localhost', user='root', password='bobai123', charset='utf8mb4') 
>>>>>>> 0798d4f6573107af9ec183814b2a5dac4d52f656
cursor = conn.cursor() 

#DB 만들기
#sql = 'Drop database bobai_web'
sql = "CREATE DATABASE bobai3" 
cursor.execute(sql)
conn.commit() 
conn.close() 


conn = pymysql.connect(host='localhost', user='root', password='rkdaudtjr1!', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()


## 테이블 만들기
<<<<<<< HEAD
sql = '''CREATE TABLE pair_info (
    id char(50) NOT NULL PRIMARY KEY,
    token0_name varchar(250),
    token1_name varchar(250),
    token00_id char(50) NOT NULL,
    token00_name varchar(250),
    token00_symbol varchar(250),
    token00_creator char(50),
    token00_decimals int,
    reserve_ETH float,
    tx_count int,
    created_at_timestamp char(15),
    is_change Bool,
    is_scam Bool
=======
sql = '''CREATE TABLE pairInfo (
    id char(50) NOT NULL PRIMARY KEY,
    stoken0Name varchar(50),
    stoken1Name varchr(50),
    stoken00Id char(50) NOT NULL,
    stoken00Name varchar(100),
    stoken00Symbol varchar(100),
    stoken00Creator char(50),
    itoken00Decimals int,
    nreserveETH float,
    itxCount int,
    screatedAtTimestamp char(15),
    bisChange Bool,
    bisScam Bool,
>>>>>>> 0798d4f6573107af9ec183814b2a5dac4d52f656
) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
''' 
##
cursor.execute(sql) 


#API로 데이터 불러오고
<<<<<<< HEAD
datas = pd.read_csv('./files/Pairs_v2.7.csv',encoding='utf-8-sig').to_dict('records')

sql = '''
INSERT INTO pair_info(id, token0_name,token1_name, token00_id, token00_name, token00_symbol, token00_creator, token00_decimals, reserve_ETH, tx_count, created_at_timestamp, is_change, is_scam) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''
=======
datas = pd.read_csv('Pairs_v2.6.csv',encoding='utf-8-sig').to_dict('records')

#예제...
#sql = "delete from pair_info;"
#sql = "ALTER TABLE table_name MODIFY COLUMN ex_column varchar(16) NULL;"
#sql = "ALTER table pair_INFO modify column name varchar(100);"
#sql = "Alter table pair_INfo modify column symbol varchar(100);"
#sql = "INSERT INTO user (email, department) VALUES (%s, %s)"
#cursor.execute(sql)

#저장하기 .. 
sql = '''
INSERT INTO Pair_INFO(id, stoken0Name,stoken1Name, stoken00Id, stoken00Name, stoken00Symbol, stoken00Creator, stoken00Decimals, nreserveETH, itxCount, screatedAtTimestamp, bisChange, bisScam) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''


>>>>>>> 0798d4f6573107af9ec183814b2a5dac4d52f656
for data in datas:
    try:
        id = data['id']
        token0_name = data['token0.name']
        token1_name = data['token1.name']
        token00_id = data['token00.id']
        token00_name = data['token00.name']
        token00_symbol = data['token00.symbol']
        token00_creator = data['creator_address']
        token00_decimals = data['token00.decimals']
        reserveETH = data['reserveETH']
        txCount = data['txCount']
        createdAtTimestamp = data['createdAtTimestamp']
        isChange = False
        isScam = False

        cursor.execute(sql,(id,token0_name,token1_name,token00_id,token00_name,token00_symbol,token00_creator,token00_decimals,reserveETH,txCount,createdAtTimestamp,isChange,isScam)) 
    except Exception as e:
        print(e)
        

conn.commit()
conn.close() 
<<<<<<< HEAD



try:
    conn = pymysql.connect(host='localhost',user='root',password='rkdaudtjr1!',db = 'bobai3',charset='utf8mb4')
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
        lp_creator_holding_ratio double,
        burn_ratio double,
        token_creator_holding_ratio double,
        PRIMARY KEY (token_id),
        FOREIGN KEY (pair_id) REFERENCES pair_info (id)
    ) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    ''' 
    cursor.execute(sql) 



except:
    print('ai feature table already exists')


sql = '''
INSERT INTO ai_feature(token_id, pair_id, mint_count, swap_count, burn_count, active_period, 
mint_mean_period, swap_mean_period, burn_mean_period, swap_in, swap_out, lp_lock_ratio, lp_avg, lp_std, 
lp_creator_holding_ratio, burn_ratio, token_creator_holding_ratio ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
'''
for data in datas:
    try:
        token_id = data['token00.id']
        pair_id = data['id']
        mint_count = data['mint_count']
        swap_count = data['swap_count']
        burn_count = data['burn_count']
        active_period = data['active_period']
        mint_mean_period = data['mint_mean_period']
        swap_mean_period = data['swap_mean_period']
        burn_mean_period = data['burn_mean_period']
        swap_in = data['swapIn']
        swap_out = data['swapOut']
        lp_lock = data['Lock_ratio']
        lp_avg = data['LP_avg']
        lp_std = data['LP_stdev']
        lp_creator_holding_ratio = data['LP_Creator_ratio']
        burn_ratio = data['burn_ratio']
        token_creator_holding_ratio = data['creator_ratio']
        cursor.execute(sql,(token_id,pair_id,mint_count,swap_count,burn_count,active_period,mint_mean_period,swap_mean_period,burn_mean_period,swap_in,swap_out,lp_lock,lp_avg,lp_std,lp_creator_holding_ratio,burn_ratio,token_creator_holding_ratio)) 
    except Exception as e:
        print(e)
        

conn.commit()
conn.close() 
=======
>>>>>>> 0798d4f6573107af9ec183814b2a5dac4d52f656
