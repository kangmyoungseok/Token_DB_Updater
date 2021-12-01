import pymysql
import pandas as pd
from tqdm import tqdm
conn = pymysql.connect(host='localhost',user='root',password='bobai123',db='bobai3',charset='utf8mb4')
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from ai_feature join pair_info on ai_feature.pair_id = pair_info.id order by pair_info.created_at_timestamp desc limit 0,1500" 
cursor.execute(sql)
datas = cursor.fetchall()
for data in tqdm(datas,desc="prcessing"):
    creator = data['token00_creator']
    sql1 = "select count(*) from pair_info where token00_creator = %s" 
    cursor.execute(sql1,creator)
    number = cursor.fetchall()[0]['count(*)']
    sql2 = "update ai_feature set number_of_token_creation_of_creator = %s where token_id = %s"
    cursor.execute(sql2,(number,data['token00_id']))

conn.commit()
conn.close()