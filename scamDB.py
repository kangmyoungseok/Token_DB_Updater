#일단 메인을 생각해보면..

# 1. 주기적으로 스캠인지 판단한다. 
# 

### 스캠 판단 로직

import pandas as pd
from lib.FeatureLib import *
from tqdm import tqdm

datas = pd.read_csv('./files/Pairs_v2.7.csv',encoding='utf-8-sig').to_dict('records')
#스캠인지 판단하는 코드 짜기

scam_list = []
count = 0

for data in tqdm(datas,desc="processing"):
    #현재 남은 이더가 1이상인 애들은 걍 패스하고
    count = count+1
    #중간저장
    if( int(count % 5000) == 0 ):
        pd.DataFrame(datas).to_csv('./drive/MyDrive/Pairs_v2.8.csv',encoding='utf-8-sig',index=False)
        pd.DataFrame(scam_list).to_csv('./drive/MyDrive/Scam_v1.0.csv',encoding='utf-8-sig',index=False)
    if(data['reserveETH'] > 1):
        data['is_scam'] = False
        continue

    try:   
        pair_address = data['id']
        token_id = data['token00.id']

        #TheGraph API를 이용해서 하나의 페어에 대한 쌍들을 전부 메모리에 올려놓고. 시작
        mint_data_transaction = call_theGraph_mint(pair_address)
        swap_data_transaction = call_theGraph_swap(pair_address)
        burn_data_transaction = call_theGraph_burn(pair_address)

        rugpull_timestamp, rugpull_change, is_rugpull, before_rugpull_Eth, after_rugpull_Eth,rugpull_method,tx_id = get_rugpull_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction,token_index(data))
        if(is_rugpull == True):
            scam_list.append({'token_id':token_id,'pair_id':pair_address,'tx_id':tx_id, 'rugpull_timestamp' :rugpull_timestamp,'beforeETH':before_rugpull_Eth,'afterETH':after_rugpull_Eth })
            data['is_scam'] = True
        else:
            data['is_scam'] = False

    except Exception as e:
        print(e)

pd.DataFrame(datas).to_csv('./drive/MyDrive/Pairs_v2.8.csv',encoding='utf-8-sig',index=False)
pd.DataFrame(scam_list).to_csv('./drive/MyDrive/Scam_v1.0.csv',encoding='utf-8-sig',index=False)