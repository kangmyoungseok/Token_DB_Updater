import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql = "delete from graph_table where pair_id = %s"

delete_list = [
'0xd4b1ae86ca316eb1d651ab31afe867fc2b607ca4',
'0x07372315c172f18d3136d72c150164173a010706'
]

for data in delete_list:
    cursor.execute(sql,data)
conn.commit()


