import pymysql
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()


## 테이블 만들기
sql = '''CREATE TABLE contract_group(
    group_id tinyint,
    contract_address char(50),
    count int,
    PRIMARY KEY(group_id)
) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
'''
cursor.execute(sql) 

