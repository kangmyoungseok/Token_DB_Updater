import pymysql 

conn = pymysql.connect(host='localhost', user='root', password='rkdaudtjr1!', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info order by created_at_timestamp"
cursor.execute(sql)
datas = cursor.fetchall()

sql2 = "select * from ai_feature "
cursor.execute(sql2)
datas2 = cursor.fetchall()

sql3= "alter table ai_feature ADD COLUMN created_at_timestamp int"
sql4= "alter table ai_feature ADD COLUMN number_of_token_creation_of_creator int"
cursor.execute(sql3)
cursor.execute(sql4)

timestamp_list = {}
creator_list = []
token_creator_list = {}
for data in datas:
    timestamp_list[data['id']] = data['created_at_timestamp']
    token_creator_list[data['id']] = data['token00_creator']
    creator_list.append(data['token00_creator']) 
    





sql5 = "update ai_feature set created_at_timestamp = %s ,number_of_token_creation_of_creator = %s where pair_id = %s"
for data in datas2:
    pair_id = data['pair_id']
    timestamp = timestamp_list[pair_id]
    numbers = creator_list.count(token_creator_list[data['pair_id']])
    try:
        cursor.execute(sql5,(timestamp,numbers,pair_id))
    except Exception as e:
        print(e)
        print(data['pair_id'])

conn.commit()
conn.close()
