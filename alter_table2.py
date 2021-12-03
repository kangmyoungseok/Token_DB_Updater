import pymysql 

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "alter table graph_table add column current_score tinyint"
cursor.execute(sql)

sql2 = "select * from graph_table "
cursor.execute(sql2)
datas2 = cursor.fetchall()


sql3 = "update graph_table set current_score = %d where token_id = '%s'"
for data in datas2:
    ai_idx = 'ai' + str(data['idx'])
    sql4 = sql3 % (data[ai_idx],data['token_id'])
    sql4
    cursor.execute(sql4)
    
conn.commit()

