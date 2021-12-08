import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
#sql = "alter table ai_feature add column unlock_date int"
#cursor.execute(sql)

sql2 = "select * from ai_feature join pair_info on pair_info.id = ai_feature.pair_id where is_scam=0 and ai_feature.lp_lock_ratio > 0 and (unlock_date = 0 or unlock_date = NULL)"
cursor.execute(sql2)
datas = cursor.fetchall()


sql4 = "update ai_feature set unlock_date = %s,lp_lock_ratio = %s where token_id = %s"

for data in tqdm(datas,desc="get unlock_time"):
    try:
        holders = get_holders(data['id'])
        lp_lock_ratio = get_Lock_ratio(holders)
        if(lp_lock_ratio > 0):    
            unlock_date = int(get_unlock_date(holders,data['token00_creator']))
        else:
            unlock_date = 0
        print(unlock_date)
        
        cursor.execute(sql4,(unlock_date,lp_lock_ratio,data['token_id']))
        conn.commit()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print('그만하기.!')
        break

conn.commit()
