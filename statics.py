import pymysql 
from lib.FeatureLib import *
from tqdm import tqdm

conn = pymysql.connect(host='localhost', user='root', password='bobai123', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)

# 12.5 ~ 12.12 일 까지의 토큰에 대해서 정확도를 분석한다.

# 라벨링이 1로 되었을 때의 정확도
# 라벨링이 0으로 되었을 때의 정확도

sql = "select * from pair_info join graph_table on pair_info.id = graph_table.pair_id where created_at_timestamp > 1638630000 and created_at_timestamp <1639234800"
cursor.execute(sql)
datas= cursor.fetchall()


len(datas)

scam_predict_list = []
good_predict_list = []
for data in datas:
    if(data['graph_table.current_score']  > 50):
        scam_predict_list.append(data)
    else:
        good_predict_list.append(data)

correct = 0
for data in scam_predict_list:
    if(data['is_scam'] == 1):
        correct = correct + 1

print("스캠 예측 정탐 [%d / %d ] " % (correct,len(scam_predict_list)))
print("스캠 예측 오탐 [%d / %d ] " % (len(scam_predict_list) - correct , len(scam_predict_list)))

correct = 0
for data in good_predict_list:
    if(data['is_scam'] == 0 ):
        correct = correct + 1

print("정상 예측 정탐 : [%d / %d ]" % (correct, len(good_predict_list)))
print("정상 예측 오탐 : [%d / %d ]" % (len(good_predict_list) - correct), len(good_predict_list))


