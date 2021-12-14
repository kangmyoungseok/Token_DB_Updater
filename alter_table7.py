import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql = "alter table pair_info add column current_score tinyint"
cursor.execute(sql)

sql2 = "select * from pair_info where is_scam = 0 "
cursor.execute(sql2)
datas = cursor.fetchall()

sql3 = "select * from pair_info join graph_table on pair_info.id = graph_table.pair_id where is_scam=0"
cursor.execute(sql3)
datas2 = cursor.fetchall()

score_list = []
for data in datas2:
    score_list.append( { data['id'] : data['graph_table.current_score']  } )


sql4 = "update pair_info set current_score = %s where id = %s"
for data in datas:
    try:
        current_score = score_list[data['id']]
    except:
        current_score = -1
    finally:
        cursor.execute(sql4,(current_score,data['id']))
        conn.commit()