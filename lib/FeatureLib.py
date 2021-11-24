from lib.Thegraph import *
import json
from bs4 import BeautifulSoup
import re
from math import sqrt

######################## 상수 값들 저장하는 공간 ##########################
proxy_contracts = [
'0x5e5a7b76462e4bdf83aa98795644281bdba80b88',
'0x000000000092c287eb63e8c2c30b4a74787054f8',
'0x0f4676178b5c53ae0a655f1b19a96387e4b8b5f2',
'0xdf65f4e6f2e9436bc1de1e00661c7108290e8bd3',
'0xdb73dde1867843fdca5244258f2fd4b6dc7b154e',
'0xbdb1127bd15e76d7e4d3bc4f6c7801aa493e03f0',
'0x8f84c1d37fa5e21c81a5bf4d3d5f2e718a2d8eb4',
'0x908521c8e53e9bb3b8b9df51e2c6dd3079549382',
'0x85aa7f78bdb2de8f3e0c0010d99ad5853ffcfc63',
'0x909d05f384d0663ed4be59863815ab43b4f347ec',
'0xb4a2810e9d0f1d4d2c0454789be80aaeb9188480',
'0x96fc64f7fe4924546b9204fe22707e3df04be4c8',
'0x226e390751a2e22449d611bac83bd267f2a2caff'
]

Locker_address = [
'0x663a5c229c09b049e36dcc11a9b0d4a8eb9db214',
'0xc77aab3c6d7dab46248f3cc3033c856171878bd5',
'0xDBF72370021baBAfbCeb05aB10f99Ad275c6220A',
'0x17e00383A843A9922bCA3B280C0ADE9f8BA48449',
'0xE2fE530C047f2d85298b07D9333C05737f1435fB',
'0xC77aab3c6D7dAb46248F3CC3033C856171878BD5',
'0x1Ba00C14F9E8D1113028a14507F1394Dc9310fbD',
'0x000000000000000000000000000000000000dead' ]

Burn_address = [
  '0x0000000000000000000000000000000000000000',
  '0x0000000000000000000000000000000000000001',
  '0x0000000000000000000000000000000000000002',
  '0x0000000000000000000000000000000000000003',
  '0x0000000000000000000000000000000000000004',
  '0x0000000000000000000000000000000000000005',
  '0x0000000000000000000000000000000000000006'
  '0x0000000000000000000000000000000000000007'
  '0x0000000000000000000000000000000000000008'
  '0x0000000000000000000000000000000000000009'
  '0x000000000000000000000000000000000000000a'
  '0x000000000000000000000000000000000000000b',
  '0x000000000000000000000000000000000000000c',
  '0x000000000000000000000000000000000000000d',
  '0x000000000000000000000000000000000000000e',
  '0x000000000000000000000000000000000000000f',
  '0x000000000000000000000000000000000000dead'
]

################################################################################




#################################### 함수들 구현하는 공간 #############################################


def get_creatorAddress(pair_id,token_id):
    repos_url = 'https://api.ethplorer.io/getAddressInfo/'+token_id+'?apiKey=EK-4L18F-Y2jC1b7-9qC3N'
    response = requests.get(repos_url).text
    repos = json.loads(response)    #json 형태로 token_id에 해당하는 정보를 불러온다.
    
    try:
        creator_address = repos['contractInfo']['creatorAddress']
        print('find by ethplorer :' + token_id)
    except:     #오류가 나면 이더스캔에서 크롤링
         url = 'https://etherscan.io/address/'+token_id
         try:
             response = requests.get(url,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'})
             page_soup = BeautifulSoup(response.text, "html.parser")
             Transfers_info_table_1 = str(page_soup.find("a", {"class": "hash-tag text-truncate"}))
             creator_address = re.sub('<.+?>', '', Transfers_info_table_1, 0).strip()
             print('find by etherscan :' + token_id)
         except Exception as e:  #이더스캔 크롤링까지 에러나면 'Error'로 표시
              print(e)
              creator_address = 'Fail to get Creator Address'
    
    if creator_address in proxy_contracts:
        query = mint_query_first % pair_id
        response = run_query(query)
        creator_address = response['data']['mints'][0]['to']
    
    return creator_address

def get_holders(token_id):
    repos_url = 'https://api.ethplorer.io/getTopTokenHolders/'+token_id+'?apiKey=EK-4L18F-Y2jC1b7-9qC3N&limit=100'
    response = requests.get(repos_url)
    if(response.status_code == 400):
        return []
    repos = json.loads(response.text)    #json 형태로 token_id에 해당하는 정보를 불러온다.
    return repos['holders']

def calc_LP_distribution(holders):
    count = 0
    for holder in holders:
        if(holder['share'] < 0.01 ):
            break
        count = count +1

    LP_avg = 100 / count
    var = 0
    for i in range(count):
        var = var + (holders[i]['share'] - LP_avg) ** 2
    
    LP_stdev = sqrt(var)

    return LP_avg,LP_stdev

def get_Lock_ratio(holders):
    for holder in holders:
        if(holder['address'] in Locker_address):
            return holder['share']
    
    return 0

def get_Creator_ratio(holders,creator_address):
    for holder in holders:
        if(holder['address'] == creator_address):
            return holder['share']
    return 0

def call_theGraph_mint(pair_id):
    mint_array = [] 
    timestamp = 0
    try:
      while(True):
        query = mint_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['mints']) < 1000): # 1000개 미만이니까 끝낸다.
          mint_array.extend(result['data']['mints'])
          break

        mint_array.extend(result['data']['mints'])
        timestamp = result['data']['mints'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_swap')
      print(e)
      
    return mint_array

def call_theGraph_swap(pair_id):
    swap_array = [] 
    timestamp = 0
    try:
      while(True):
        query = swap_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['swaps']) < 1000): # 1000개 미만이니까 끝낸다.
          swap_array.extend(result['data']['swaps'])
          break

        swap_array.extend(result['data']['swaps'])
        timestamp = result['data']['swaps'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_swap')
      print(e)
      
    return swap_array

def call_theGraph_burn(pair_id):
    burn_array = [] 
    timestamp = 0
    try:
      while(True):
        query = burn_query_template % (pair_id,timestamp)
        result = run_query(query)

        if(len(result['data']['burns']) < 1000): # 1000개 미만이니까 끝낸다.
          burn_array.extend(result['data']['burns'])
          break

        burn_array.extend(result['data']['burns'])
        timestamp = result['data']['burns'][999]['timestamp']      
    except Exception as e:
      print('error in theGraph_burn')
      print(e)
      
    return burn_array


def get_mint_mean_period(mint_data_transaction,initial_timestamp):
    count = len(mint_data_transaction)
    if(count == 0):
      return 0
    mint_time_add = 0
    for transaction in mint_data_transaction:
      mint_time_add = mint_time_add + int(transaction['timestamp']) - initial_timestamp
    return mint_time_add / count

def get_swap_mean_period(swap_data_transaction,initial_timestamp):
    count = len(swap_data_transaction)
    if(count == 0):
      return 0
    swap_time_add = 0
    for transaction in swap_data_transaction:
      swap_time_add = swap_time_add +  int(transaction['timestamp']) - initial_timestamp
    return swap_time_add / count

def get_burn_mean_period(burn_data_transaction,initial_timestamp):
    count = len(burn_data_transaction)
    if(count == 0):
      return 0
    burn_time_add = 0
    for transaction in burn_data_transaction:
      burn_time_add = burn_time_add + int(transaction['timestamp']) - initial_timestamp
    return burn_time_add / count

def swap_IO_rate(swap_data_transaction,index):
  swapIn = 0
  swapOut = 0
  if(index == 1): #amount0이 이더.
    for data in swap_data_transaction:
      if(data['amount0In'] == '0'): #amount0Out이 0이 아니란 말. 
        swapOut = swapOut + 1
      else:   
        swapIn = swapIn + 1
  else:         #amount1이 이더
    for data in swap_data_transaction:
      if(data['amount1In'] == '0'):
        swapOut = swapOut + 1
      else:
        swapIn = swapIn +1
  
  return swapIn,swapOut 

def get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction):
  #mint_data_transaction은 0일 수가 없다. 
  swap_len = len(swap_data_transaction)
  burn_len = len(burn_data_transaction)
  #Case 1 Swap / Burn 전부 0 인경우
  if(swap_len == 0 and burn_len == 0):
    return int(mint_data_transaction[-1]['timestamp'])
  #Case 2 Swap_transaction이 0 인경우
  if(swap_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp']))
  #Case 3 Burn Transaction이 0 인경우
  if(burn_len == 0):
    return int(max(mint_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))
  #Case 4 전부다 있는 경우
  return int(max(mint_data_transaction[-1]['timestamp'],burn_data_transaction[-1]['timestamp'],swap_data_transaction[-1]['timestamp']))

def token_index(data):
    if(data['token0.name'] == 'Wrapped Ether'):
        return 1
    else:
        return 0

def get_burn_ratio(holders):
  for holder in holders:
    if(holder['address'] in Burn_address):
      return holder['share']
    
  return 0

def get_creator_ratio(holders,creator_address):
  for holder in holders:
    if(holder['address'] == creator_address):
      return holder['share']
  
  return 0
