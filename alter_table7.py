import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql = "update pair_info set current_score = -1"
cursor.execute(sql)


sql1 = "select id,graph_table.current_score from pair_info join graph_table on pair_info.id = graph_table.pair_id where is_scam=0"
cursor.execute(sql1)
datas2 = cursor.fetchall()

sql2 ="update pair_info set current_score = %s where id = %s"
for data in datas2:
    cursor.execute(sql2,(data['current_score'],data['id']))


