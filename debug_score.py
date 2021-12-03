import pymysql 
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

sql = "select * from graph_table join pair_info on pair_info.id = graph_table.pair_id"
cursor.execute(sql)
datas = cursor.fetchall()

pd.DataFrame(datas).to_csv('debug.csv',encoding='utf-8-sig')
