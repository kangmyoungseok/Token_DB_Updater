import pymysql
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor()


## 테이블 만들기
sql = '''CREATE TABLE graph_table(
    token_id char(50),
    pair_id char(50),
    idx TINYINT,
    is_latest TINYINT,
    ai0 TINYINT, ai1 TINYINT, ai2 TINYINT,
    ai3 TINYINT, ai4 TINYINT, ai5 TINYINT,
    ai6 TINYINT, ai7 TINYINT, ai8 TINYINT,
    ai9 TINYINT, ai10 TINYINT, ai11 TINYINT,
    ai12 TINYINT, ai13 TINYINT, ai14 TINYINT,
    ai15 TINYINT, ai16 TINYINT, ai17 TINYINT,
    ai18 TINYINT, ai19 TINYINT, ai20 TINYINT,
    ai21 TINYINT, ai22 TINYINT, ai23 TINYINT,
    eth0 float, eth1 float, eht2 float,
    eth3 float, eth4 float, eht5 float,
    eth6 float, eth7 float, eht8 float,
    eth9 float, eth10 float, eht11 float,
    eth12 float, eth13 float, eht14 float,
    eth15 float, eth16 float, eht17 float,
    eth18 float, eth19 float, eht20 float,
    eth21 float, eth22 float, eht23 float,
    FOREIGN KEY (pair_id) REFERENCES pair_info (id)
) CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
'''
cursor.execute(sql) 
