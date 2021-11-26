import pymysql
import pandas as pd
from lib.Thegraph import *
from lib.FeatureLib import *
from tqdm import tqdm

datas = pd.read_csv('./files/Pairs_v2.5.csv',encoding='utf-8-sig').to_dict('records')
error_list = []

for data in tqdm(datas,desc="processing rate"):
    try:
        # Feature Part 1
        holders = get_holders(data['id'])
        Lock_ratio = get_Lock_ratio(holders)
        LP_avg, LP_stdev = calc_LP_distribution(holders)
        LP_Creator_ratio = get_Creator_ratio(holders,data['creator_address'])
        data['holders'] = holders
        data['Lock_ratio'] = Lock_ratio
        data['LP_avg'] = LP_avg
        data['LP_stdev'] = LP_stdev
        data['LP_Creator_ratio'] = LP_Creator_ratio
        
        # Feature Part 2
        pair_address = data['id']
        mint_data_transaction = call_theGraph_mint(pair_address)
        swap_data_transaction = call_theGraph_swap(pair_address)
        burn_data_transaction = call_theGraph_burn(pair_address)

        mint_count = len(mint_data_transaction)
        swap_count = len(swap_data_transaction)
        burn_count = len(burn_data_transaction)

        initial_timestamp = int(mint_data_transaction[0]['timestamp'])
        last_timestamp = get_last_timestamp(mint_data_transaction,swap_data_transaction,burn_data_transaction)
        active_period = last_timestamp - initial_timestamp
        mint_mean_period = int(get_mint_mean_period(mint_data_transaction,initial_timestamp))
        swap_mean_period = int(get_swap_mean_period(swap_data_transaction,initial_timestamp))
        burn_mean_period = int(get_burn_mean_period(burn_data_transaction,initial_timestamp))

        swapIn,swapOut = swap_IO_rate(swap_data_transaction,token_index(data))

        data['mint_count'] = mint_count
        data['swap_count'] = swap_count
        data['burn_count'] = burn_count
        
        data['active_period'] = active_period
        data['mint_mean_period'] = mint_mean_period
        data['swap_mean_period'] = swap_mean_period
        data['burn_mean_period'] = burn_mean_period

        data['swapIn'] = swapIn
        data['swapOut'] = swapOut

        # Feature part 3
        token_holders = get_holders(data['token00.id'])   
        burn_ratio = get_burn_ratio(token_holders)
        creator_ratio = get_creator_ratio(token_holders,data['creator_address'])

        data['token_holders'] = token_holders
        data['burn_ratio'] = burn_ratio
        data['creator_ratio'] = creator_ratio

    
    except Exception as e:
        data['error'] = e
        print(e)

pd.DataFrame(datas).to_csv('./drive/MyDrive/pairs_v2.6.csv',encoding='utf-8-sig',index=False)