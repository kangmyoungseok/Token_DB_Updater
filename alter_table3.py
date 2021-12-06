import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm
conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "alter table ai_feature add column unlock_date int"
cursor.execute(sql)

sql2 = "select * from ai_feature join pair_info on pair_info.id = ai_feature.pair_id where is_scam=0 and pair_info.created_at_timestamp >= 1629978354"
cursor.execute(sql2)
datas = cursor.fetchall()

sql3 = "update ai_feature set unlock_date = 0 where created_at_timestamp < 1629978354 "
cursor.execute(sql3)
conn.commit()


sql4 = "update ai_feature set unlock_date = %s where token_id = %s"
data = datas[0]

for data in tqdm(datas,desc="get unlock_time"):
    holders = get_holders(data['id'])
    lp_lock_ratio = get_Lock_ratio(holders)
    if(lp_lock_ratio > 0):    
        unlock_date = int(get_unlock_date(holders,data['token00_creator']))
    else:
        unlock_date = 0
    print(unlock_date)
    
    cursor.execute(sql4,(unlock_date,data['token_id']))

conn.commit()
