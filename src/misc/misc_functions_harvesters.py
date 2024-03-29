import math
import pandas as pd
import seaborn as sns
import numpy as np
import random
import matplotlib.pyplot as plt
import requests
import json



fud_harvester = pd.read_csv("data/fud_harvester.csv")
fomo_harvester = pd.read_csv("data/fomo_harvester.csv")
alpha_harvester = pd.read_csv("data/alpha_harvester.csv")
kek_harvester = pd.read_csv("data/kek_harvester.csv")

fud_harvester['Build Time (Days)'] = fud_harvester['Built Time (Blocks) ']/40000
fomo_harvester['Build Time (Days)'] = fomo_harvester['Built Time (Blocks)']/40000
alpha_harvester['Build Time (Days)'] = alpha_harvester['Built Time (Blocks)']/40000
kek_harvester['Build Time (Days)'] = kek_harvester['Built Time (Blocks)']/40000

fud_reservoir = pd.read_csv("data/fud_reservoir.csv")
fomo_reservoir = pd.read_csv("data/fomo_reservoir.csv")
alpha_reservoir = pd.read_csv("data/alpha_reservoir.csv")
kek_reservoir = pd.read_csv("data/kek_reservoir.csv")

fud_reservoir['Build Time (Days)'] = fud_reservoir['Built Time (Blocks)']/40000
fomo_reservoir['Build Time (Days)'] = fomo_reservoir['Built Time (Blocks)']/40000
alpha_reservoir['Build Time (Days)'] = alpha_reservoir['Built Time (Blocks)']/40000
kek_reservoir['Build Time (Days)'] = kek_reservoir['Built Time (Blocks)']/40000


avg_alchemica_df = pd.read_csv("data/avg_parcel_yield.csv")
avg_alchemica_df = avg_alchemica_df.replace(',','', regex=True)
avg_alchemica_df.columns = ['ParcelType', 'FUD', 'FOMO', 'ALPHA', 'KEK']

cols = ['FUD', 'FOMO', 'ALPHA', 'KEK']
avg_alchemica_df[cols] = avg_alchemica_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)


avg_alchemica_per_parcel_dict = {
    'humble' : {
        'FUD': 7077, 'FOMO': 3539, 'ALPHA': 1769, 'KEK': 708
    },
    'reasonable': {
        'FUD': 28308, 'FOMO': 14154, 'ALPHA': 7077, 'KEK': 2831
    },
    'spacious': {
        'FUD': 226465, 'FOMO': 113233, 'ALPHA': 56616, 'KEK': 22647
    }
}


fud_factor = 1.0
fomo_factor = 2.0
alpha_factor = 4.0
kek_factor = 10.0

try:
    URL = "https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi-fud%2Caavegotchi-fomo%2Caavegotchi-alpha%2Caavegotchi-kek%2Caavegotchi&vs_currencies=usd"
    result = requests.get(url = URL).json()

    fud_factor = 1.0
    fomo_factor = result['aavegotchi-fomo']['usd']/result['aavegotchi-fud']['usd']
    alpha_factor = result['aavegotchi-alpha']['usd']/result['aavegotchi-fud']['usd']
    kek_factor = result['aavegotchi-kek']['usd']/result['aavegotchi-fud']['usd']
except:
    print("unable to get token factors from the API")
    

alchemica_factor_dict = {
    'FUD': fud_factor,
    'FOMO': fomo_factor,
    'ALPHA': alpha_factor,
    'KEK': kek_factor
}


def compute_cost_dict_for_harvestor_reservoirs(df):
    return { df['Level'][i]:
                          fud_factor*int(df['FUD'][i])+
                          fomo_factor*int(df['FOMO'][i])+
                          alpha_factor*int(df['ALPHA'][i])+
                          kek_factor*int(df['KEK'][i]) 
                          for i in range(df.shape[0]) }

fud_harvester_cost_dict = compute_cost_dict_for_harvestor_reservoirs(fud_harvester)
fomo_harvester_cost_dict = compute_cost_dict_for_harvestor_reservoirs(fomo_harvester)
alpha_harvester_cost_dict = compute_cost_dict_for_harvestor_reservoirs(alpha_harvester)
kek_harvester_cost_dict = compute_cost_dict_for_harvestor_reservoirs(kek_harvester)

fud_reservoir_cost_dict = compute_cost_dict_for_harvestor_reservoirs(fud_reservoir)
fomo_reservoir_cost_dict = compute_cost_dict_for_harvestor_reservoirs(fomo_reservoir)
alpha_reservoir_cost_dict = compute_cost_dict_for_harvestor_reservoirs(alpha_reservoir)
kek_reservoir_cost_dict = compute_cost_dict_for_harvestor_reservoirs(kek_reservoir)


def compute_harvestor_harvestrate_dict(df):
    return {
        df['Level'][i]:df['HarvestRate/Day'][i]
        for i in range(9)
    }

fud_harvester_harvestrate = compute_harvestor_harvestrate_dict(fud_harvester)
fomo_harvester_harvestrate = compute_harvestor_harvestrate_dict(fomo_harvester)
alpha_harvester_harvestrate = compute_harvestor_harvestrate_dict(alpha_harvester)
kek_harvester_harvestrate = compute_harvestor_harvestrate_dict(kek_harvester)

def compute_harvestor_reservoir_build_time_dict(df):
    return {
        df['Level'][i]:df['Build Time (Days)'][i]
        for i in range(9)
    }

fud_harvester_build_time = compute_harvestor_reservoir_build_time_dict(fud_harvester)
fomo_harvester_build_time = compute_harvestor_reservoir_build_time_dict(fomo_harvester)
alpha_harvester_build_time = compute_harvestor_reservoir_build_time_dict(alpha_harvester)
kek_harvester_build_time = compute_harvestor_reservoir_build_time_dict(kek_harvester)

fud_reservoir_build_time = compute_harvestor_reservoir_build_time_dict(fud_reservoir)
fomo_reservoir_build_time = compute_harvestor_reservoir_build_time_dict(fomo_reservoir)
alpha_reservoir_build_time = compute_harvestor_reservoir_build_time_dict(alpha_reservoir)
kek_reservoir_build_time = compute_harvestor_reservoir_build_time_dict(kek_reservoir)

def compute_reservoir_capacity_dict(df):
    return {
        df['Level'][i]:df['Capacity'][i]
        for i in range(9)
    }


fud_reservoir_capacity = compute_reservoir_capacity_dict(fud_reservoir)
fomo_reservoir_capacity = compute_reservoir_capacity_dict(fomo_reservoir)
alpha_reservoir_capacity = compute_reservoir_capacity_dict(alpha_reservoir)
kek_reservoir_capacity = compute_reservoir_capacity_dict(kek_reservoir)


def harvestor_cost_finder(x):
    return {
        'FUD': fud_harvester_cost_dict,
        'FOMO': fomo_harvester_cost_dict,
        'ALPHA': alpha_harvester_cost_dict,
        'KEK': kek_harvester_cost_dict
    }.get(x)


def reservoir_cost_finder(x):
    return {
        'FUD': fud_reservoir_cost_dict,
        'FOMO': fomo_reservoir_cost_dict,
        'ALPHA': alpha_reservoir_cost_dict,
        'KEK': kek_reservoir_cost_dict
    }.get(x)


def harvestor_harvestrate_finder(x):
    return {
        'FUD': fud_harvester_harvestrate,
        'FOMO': fomo_harvester_harvestrate,
        'ALPHA': alpha_harvester_harvestrate,
        'KEK': kek_harvester_harvestrate
    }.get(x)


def reservoir_capacity_finder(x):
    return {
        'FUD': fud_reservoir_capacity,
        'FOMO': fomo_reservoir_capacity,
        'ALPHA': alpha_reservoir_capacity,
        'KEK': kek_reservoir_capacity
    }.get(x)



def harvestor_build_time_finder(x):
    return {
        'FUD': fud_harvester_build_time,
        'FOMO': fomo_harvester_build_time,
        'ALPHA': alpha_harvester_build_time,
        'KEK': kek_harvester_build_time
    }.get(x)


def reservoir_build_time_finder(x):
    return {
        'FUD': fud_reservoir_build_time,
        'FOMO': fomo_reservoir_build_time,
        'ALPHA': alpha_reservoir_build_time,
        'KEK': kek_reservoir_build_time
    }.get(x)


daily_reservoir_empty_frequency = 3

class HelperDictsClass:
    
    reservoir_cost_dict = None
    reservoir_capacity = None
    reservoir_build_time = None
    harvester_cost_dict = None
    harvester_build_time = None
    harvester_rate = None
    
    
    def __init__(self, alchemica_type):
        self.reservoir_cost_dict = reservoir_cost_finder(alchemica_type)
        self.reservoir_capacity = reservoir_capacity_finder(alchemica_type)
        self.reservoir_build_time = reservoir_build_time_finder(alchemica_type)
        self.harvester_cost_dict = harvestor_cost_finder(alchemica_type)
        self.harvester_build_time = harvestor_build_time_finder(alchemica_type)
        self.harvester_rate = harvestor_harvestrate_finder(alchemica_type)


helper_dicts = {
    'FUD': HelperDictsClass('FUD'),
    'FOMO': HelperDictsClass('FOMO'),
    'ALPHA': HelperDictsClass('ALPHA'),
    'KEK': HelperDictsClass('KEK')
}



def compute_profit_for_time_T(harvestors_array, reservoirs_array, T, helper_obj, alchemica_factor, alchemica_amount):
    ## what should be the order in which harvestors and reservoirs are built, it is also important
    ## here we will first construct all reseervoirs, then all harvestors in desccending order
    
    days_passed = 0
    cost_till_now = 0
    harvest_till_now = 0
    
    for reservoir in reservoirs_array:
        cost_till_now += helper_obj.reservoir_cost_dict[reservoir]
        days_passed += helper_obj.reservoir_build_time[reservoir]
        
    #print("total reservoir cost -->", cost_till_now)
    
    for harvestor in sorted(harvestors_array, reverse=True):
        if harvestor == 0:
            continue
        
        cost_till_now += helper_obj.harvester_cost_dict[harvestor]
        days_passed += helper_obj.harvester_build_time[harvestor]
                
        harvest_till_now += alchemica_factor * helper_obj.harvester_rate[harvestor] * (T-days_passed) #TODO - also add all the time that has passed from level 1 to current upgrade
        
        
    if harvest_till_now > alchemica_amount:
        harvest_till_now = alchemica_amount
        
    #print("adding on harvestor cost -->", cost_till_now)
    #print("total harvest -->", harvest_till_now)
    
    return (harvest_till_now - cost_till_now)





def compute_reservoir_needed(harvestors_array, helper_obj):
    ## keep on upgrading the current reservoir till highest level, then start building the 2nd one
    
    reservoirs_array = []
    
    total_daily_required_capacity = 0
    
    for harvestor in harvestors_array:
        if harvestor == 0:
            continue
        total_daily_required_capacity += helper_obj.harvester_rate[harvestor]
        
    
    #print("total daily required capacity -->", total_daily_required_capacity)
    
    current_capacity = 0
    while True:
        #print("loop")
        
        if total_daily_required_capacity > daily_reservoir_empty_frequency*helper_obj.reservoir_capacity[9]: #means more than 1 reservoir is needed
            reservoirs_array.append(9) #append maximum level
            total_daily_required_capacity -= daily_reservoir_empty_frequency*helper_obj.reservoir_capacity[9]
            
        else:
            for i in range(1, 10):
                if total_daily_required_capacity < daily_reservoir_empty_frequency*helper_obj.reservoir_capacity[i]:
                    reservoirs_array.append(i)
                    return reservoirs_array
            

            

            


def compute_harvestor_reservoir_for_parcel_alchemica(parcel, alchemica_type, T, parcel_alchemica_content):
    
    harvestors_built = [0]*parcel.max_allowed_harvestors_for_alchemica(alchemica_type)
    harvestors_built[0] = 1
    reservoirs_built = [1]
    
    helper_obj = helper_dicts[alchemica_type]

    alchemica_factor = alchemica_factor_dict[alchemica_type]
    
    alchemica_amount = parcel_alchemica_content * alchemica_factor
    
    total_spent = helper_obj.harvester_cost_dict[1] + helper_obj.reservoir_cost_dict[1] #building level 1 harvestor and reservoir

    original_harvestors_array = harvestors_built.copy()
    original_reservoirs_array = reservoirs_built.copy()

    while(True):
    
        optimized_harvestors_array = original_harvestors_array.copy()
        optimized_reservoirs_array = original_reservoirs_array.copy()


        optimized_profit = compute_profit_for_time_T(optimized_harvestors_array, optimized_reservoirs_array, T, helper_obj, alchemica_factor, alchemica_amount)
        # break the loop when current state is the max profit state

#         print("----------------------------------------")
#         print("new iteration begins")
#         print("current harvestor --> ", optimized_harvestors_array)
#         print("current reservoir --> ", optimized_reservoirs_array)
#         print("current profit -->", optimized_profit)


        # calculate next options
        for i in range(len(original_harvestors_array)):

            if original_harvestors_array[i] == 9:
                continue

            #print("\nupgrading harvestor number -->", i)

            #if I upgrade this harvestor, what is the marginal cost
            new_harvestors_array = original_harvestors_array.copy()
            new_harvestors_array[i] += 1

            #print("new harvestor --> ", new_harvestors_array)


            #compute the reservoir needed
            new_reservoirs_array = compute_reservoir_needed(new_harvestors_array, helper_obj)
            #print("new reservoir --> ", new_reservoirs_array)

            #print("alchemica factor {}, alchemica amount {}".format(alchemica_factor, alchemica_amount))


            #compute the total profit of the setup
            new_profit = compute_profit_for_time_T(new_harvestors_array, new_reservoirs_array, T, 
                                                   helper_obj, alchemica_factor, alchemica_amount)

            #print("new profit -->", new_profit)


            if new_profit > optimized_profit:
                optimized_harvestors_array = new_harvestors_array.copy()
                optimized_reservoirs_array = new_reservoirs_array.copy()
                optimized_profit = new_profit


        if original_harvestors_array == optimized_harvestors_array and original_reservoirs_array == optimized_reservoirs_array:
#             print("\n---------------------------------------------------------\n")
#             print("| optimal solution found\t\t\t\t|")

#             print("| optimal solution is -->", optimized_harvestors_array, optimized_reservoirs_array, "\t\t|")
#             print("| optimal profit -->", optimized_profit, "\t\t|")
#             print("\n---------------------------------------------------------\n")

            break

        else:
            original_harvestors_array = optimized_harvestors_array.copy()
            original_reservoirs_array = optimized_reservoirs_array.copy()

    return optimized_harvestors_array, optimized_reservoirs_array, optimized_profit
    

    
def time_spent_in_construction(harvestor_array, reservoir_array, alchemica_type, num_workers):
    helper_obj = helper_dicts[alchemica_type]
    
#     print(harvestor_array)
#     print(helper_obj.harvester_build_time)
    
#     print(reservoir_array)
#     print(helper_obj.reservoir_build_time)
    
    total_time_spent = 0
    for h in harvestor_array:
        if h>0:
            for i in range(1, h+1):
                total_time_spent += helper_obj.harvester_build_time[i]
    
    
    for r in reservoir_array:
        if r>0:
            for i in range(1, r+1):
                total_time_spent += helper_obj.reservoir_build_time[i]
    
    
    
    return total_time_spent 



def total_alchemica_extracted(harvestor_array, reservoir_array, alchemica_type, T, num_workers):
    helper_obj = helper_dicts[alchemica_type]
    
    #print(helper_obj.harvester_rate)
    
    return sum([T*helper_obj.harvester_rate[k] for k in harvestor_array if k>0])




def most_profitable_alchemica(input_al, parcel_tag):
    
    avg_alchemica_per_parcel = avg_alchemica_per_parcel_dict[parcel_tag]
    
    avg_al = [avg_alchemica_per_parcel['FUD'], avg_alchemica_per_parcel['FOMO'],
             avg_alchemica_per_parcel['ALPHA'], avg_alchemica_per_parcel['KEK']]
    
    max_till_now = (input_al[0] - avg_al[0])*100/avg_al[0]
    max_tag = 'FUD'
    
    relative_margin_dict = {}
    for alchemica, x, y in zip(['FUD', 'FOMO', 'ALPHA', 'KEK'], input_al, avg_al):
        margin = (x-y)*100/y
        relative_margin_dict[alchemica] = round(margin,2)
        
    return relative_margin_dict