import pymysql 

conn = pymysql.connect(host='localhost', user='root', password='rkdaudtjr1!', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info order by created_at_timestamp"
cursor.execute(sql)
datas = cursor.fetchall()

sql2 = "select * from ai_feature "
cursor.execute(sql2)
datas2 = cursor.fetchall()

sql3= "alter table ai_feature ADD COLUMN created_at_timestamp char(15)"
cursor.execute(sql3)


timestamp_list = {}
for data in datas:
    timestamp_list[data['id']] = data['created_at_timestamp']


sql4 = "update ai_feature set created_at_timestamp = %s where pair_id = %s"
for data in datas2:
    try:
        cursor.execute(sql4,(timestamp_list[data['pair_id']],data['pair_id']))
    except Exception as e:
        print(e)
        print(data['pair_id'])

conn.commit()
conn.close()
len(datas2)