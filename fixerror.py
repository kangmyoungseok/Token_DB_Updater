#Error 수정용 파일
#DB에 Creator Address가 안들어 있는 애들이 있음.

import pymysql
import pandas as pd
from lib.FeatureLib import *

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info where token00_creator = 'None'"
sql2 = "Update pair_info set token00_creator = '%s' where token00_id = '%s'"
cursor.execute(sql)
datas = cursor.fetchall()
print(len(datas))
for data in datas:
    creator_address = get_creatorAddress(data['id'],data['token00_id'])
    print(creator_address)
    cursor.execute(sql2,(creator_address,data['token00_id']))

conn.commit()