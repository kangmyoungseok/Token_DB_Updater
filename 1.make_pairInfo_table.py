import pymysql 
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='bobai123', charset='utf8mb4') 
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
) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
''' 
##
cursor.execute(sql) 


#API로 데이터 불러오고
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
