#러그풀이 발생했는지 체크하는 로직. 이것도 한시간 마다 하면 되자나??? feature 구할때..~
#러그풀 발생하는지 체크하는건 생긴지 3달이내의 토큰에 대해서만 할까??? 아니면 좀더? 긁는건 별로 안걸리자늠? 
#여기있는 코드는 1시간 간격에서 체크할 용도 임.!
from time import time
from lib.Thegraph import *
import pymysql 
from decimal import Decimal
current_time = int(time())

query_scam_iter = '''
{
 pairs(first: 1000, orderBy: createdAtBlockNumber, orderDirection: desc, where: {createdAtTimestamp_lt:%s, reserveETH_lt:0.01}) {
   id
   reserveETH
   txCount
   createdAtTimestamp
   createdAtBlockNumber
 }
}
''' 
pairs = []
limit_time = current_time

while(1):
    query = query_scam_iter % limit_time
    result = run_query(query) 
    pairs.extend(result['data']['pairs'])
    limit_time = int(result['data']['pairs'][999]['createdAtTimestamp'])
    if( (current_time - limit_time) > 3888000):
      print(current_time - limit_time)
      break
limit_time

#자 일단 현재 이더가 0.01이상인 애들 쭉 모았고.. 음 .. !?
#DB에서도 데이터 
conn = pymysql.connect(host='localhost', user='root', password='rkdaudtjr1!', db='bobai3', charset='utf8mb4') 
cursor = conn.cursor(pymysql.cursors.DictCursor)
sql = "select * from pair_info order by created_at_timestamp desc limit 0,5000"
cursor.execute(sql)
datas = cursor.fetchall()
datas[7]

datas[4999]
sus_list = {}
for pair in pairs:
  sus_list[pair['id']] = pair['reserveETH']

for data in datas:
  if(data['is_scam'] == 1):
    continue
  try:
    before_ETH = Decimal(data['reserve_ETH'])
    current_ETH = Decimal(sus_list[data['id']])
    
    if( (current_ETH / before_ETH) < 0.01 ):
      print("러그풀 발생 before : %d , after : %d, id : %s",before_ETH,current_ETH,data['id'])

  except Exception as e:
  #  print(e)
    continue