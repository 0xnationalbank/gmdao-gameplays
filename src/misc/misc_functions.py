# misc helper functions

import math
import pandas as pd
import seaborn as sns
import numpy as np
import random
import matplotlib.pyplot as plt
import requests


BASE_RATE = [20, 10, 5, 2] #ordered by FUD, FOMO, ALPHA, KEK
plot_size_array = [1, 2, 4, 8, 16, 32, 64]
SPILLOVER_COLLECTION_RATE = 0.3 # this will depend on radius and size of parcel

URL = "https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi-fud%2Caavegotchi-fomo%2Caavegotchi-alpha%2Caavegotchi-kek%2Caavegotchi&vs_currencies=usd"
result = requests.get(url = URL).json()

fud_factor = 1.0
fomo_factor = result['aavegotchi-fomo']['usd']/result['aavegotchi-fud']['usd']
alpha_factor = result['aavegotchi-alpha']['usd']/result['aavegotchi-fud']['usd']
kek_factor = result['aavegotchi-kek']['usd']/result['aavegotchi-fud']['usd']


CHANNELING_RATE_IN_HOURS = {0: float('inf'),
    1:24, 2:18, 3:12, 4:8, 
    5:6, 6:4, 7:3, 8:2, 9:1
}


altaar_cost_df = pd.read_csv("data/altaar_cost.csv")
altaar_cost_df = altaar_cost_df.replace(',','', regex=True)

altaar_built_time_dict = { altaar_cost_df['Level'][i]: altaar_cost_df['Buid Time (Days) '][i] for i in range(altaar_cost_df.shape[0]) }
altaar_built_time_dict


altaar_built_cost_dict = { altaar_cost_df['Level'][i]: 
                          fud_factor*int(altaar_cost_df['FUD'][i])+
                          fomo_factor*int(altaar_cost_df['FOMO'][i])+
                          alpha_factor*int(altaar_cost_df['ALPHA'][i])+
                          kek_factor*int(altaar_cost_df['KEK'][i]) 
                          for i in range(altaar_cost_df.shape[0]) }
altaar_built_cost_dict


yield_at_base_rate = fud_factor*BASE_RATE[0]+ \
                    fomo_factor*BASE_RATE[1] + \
                    alpha_factor*BASE_RATE[2] + \
                    kek_factor*BASE_RATE[3]



"""
this function will be used once there is more information how spill varies according to radius
"""
def spill_radius_function(x_len, y_len):
    tmp_array = [[0]*x_len for i in range(y_len)]
    mid_x = x_len/2.0
    mid_y = y_len/2.0
    
    for i in range(x_len):
        for j in range(y_len):
            pixel_x = i+0.5
            pixel_y = j+0.5
            dist_from_mid = math.sqrt(math.pow(mid_x-pixel_x, 2) + math.pow(mid_y-pixel_y, 2))
            
            tmp_array[i][j] = dist_from_mid
    
    return tmp_array

spill_radius_function(3,3)



"""
this is a simple spill collection function which depends on size of parcel
spillover collection is 1 for 64X64
splillover collection for k X k = (k/64)*(k/64)
"""

def spill_collection_rate(x_len, y_len):
    
    return (x_len/64)*(y_len/64)




"""
This function computes yield which an altaar which generate in 1 day, given the following parameters
1. kinships of all the available gotchis
2. the level of altaar
3. dimension of the parcel

yield = frequency_of_channel x base_rate_yield x channeling_modifier x spillover_rate x collection_rate
"""

def get_yield_for_the_day(gotchi_kinship_array, altaar_level, parcel_dim):
    x, y = parcel_dim
    
    spillover_rate = (50 - (altaar_level-1)*5)/100.0
    
    channeling_modifier_array = sorted([math.sqrt(ele/50) for ele in gotchi_kinship_array], reverse=True) #start by using gotchi's who have more kinship
    
    channel_frequency = int(24/CHANNELING_RATE_IN_HOURS[altaar_level])
    
    total_yield = 0
    for i in range(min(len(gotchi_kinship_array), channel_frequency)):
        total_yield += int(channeling_modifier_array[i]*yield_at_base_rate*(1-spillover_rate) * spill_collection_rate(x, y))
    
    return total_yield

get_yield_for_the_day([500, 500], 1, [64,64])



"""
TODO: need to implement this function covering all the types of scenarios
1. day will be divided into 2 parts. one with the original altar, 2nd with the upgraded altar
2. gotchi's need to make a choice which altaar to channel, depending on how many channel frequency are available in each
3. preferably gotchi's should channel the upgraded altar
"""
def get_yield_for_the_upgrade_day(gotchi_kinship_array, altaar_level, parcel_dim, pending_built_time):
    # using the same function as of now, will work on this function later
    return get_yield_for_the_day(gotchi_kinship_array, altaar_level, parcel_dim)

get_yield_for_the_upgrade_day([500, 500], 1, [64,64], 0.3)


def future_yield_by_current_altaar(gotchi_kinship_array, altaar_level, parcel_dim, num_days):
    return get_yield_for_the_day(gotchi_kinship_array, altaar_level, parcel_dim)*num_days




"""
Given (a) number of days (b) what could be the maximum altaar built,
this function computes the maximum yield possible, and till what level should the altaar be upgraded
"""
def gameplay_v3(gotchi_kinship_array, num_days, current_altaar, parcel_dim, max_allowed_altaar):

    pending_built_time_for_next_altaar = math.inf if current_altaar >= max_allowed_altaar else altaar_built_time_dict[current_altaar+1]
    
    total_yield_till_now = 0
    
    max_expected_yield = 0
    max_yield_level = 1
    
    for i in range(num_days):
        
        if pending_built_time_for_next_altaar <=1: #altaar can be made current day
            total_yield_till_now += get_yield_for_the_upgrade_day(gotchi_kinship_array, current_altaar, parcel_dim, pending_built_time_for_next_altaar)
            total_yield_till_now -= altaar_built_cost_dict[current_altaar+1]  #reducing the total cost for building the altaar
            
            if current_altaar == max_allowed_altaar-1:
                current_altaar = current_altaar + 1
                pending_built_time_for_next_altaar = math.inf
            elif current_altaar == max_allowed_altaar:
                pending_built_time_for_next_altaar = math.inf
            else:
                current_altaar = current_altaar + 1
                pending_built_time_for_next_altaar = altaar_built_time_dict[current_altaar+1]

        else:
            total_yield_till_now += get_yield_for_the_day(gotchi_kinship_array, current_altaar, parcel_dim)
            pending_built_time_for_next_altaar -= 1
            
        #print("day {}, current level {}, pending time {}".format(i+1, current_altaar, pending_built_time_for_next_altaar))
        
        future_yield = future_yield_by_current_altaar(gotchi_kinship_array, current_altaar, parcel_dim, num_days-i-1)
                
        if total_yield_till_now + future_yield > max_expected_yield:
            max_expected_yield = total_yield_till_now + future_yield
            max_yield_level = current_altaar
    
        gotchi_kinship_array = [ele+2 for ele in gotchi_kinship_array]

    return max_expected_yield, max_yield_level

    
total_yield, altaar_level = gameplay_v3(gotchi_kinship_array=[500, 500],
            num_days=300,
            current_altaar=1,
            parcel_dim = [32, 32],
            max_allowed_altaar=3                                                
           )

#print(total_yield)



def compute_yield_dict(days, avg_gotchi):
    return {
        (8, 8): [gameplay_v3(gotchi_kinship_array=[avg_gotchi],
                                                num_days=days,
                                                current_altaar=1,
                                                parcel_dim = [8, 8],
                                                max_allowed_altaar=level+1)
                 for level in range(9)],
        (16, 16): [gameplay_v3(gotchi_kinship_array=[avg_gotchi],
                                                num_days=days,
                                                current_altaar=1,
                                                parcel_dim = [16, 16],
                                                max_allowed_altaar=level+1)
                 for level in range(9)],
        (32, 64): [gameplay_v3(gotchi_kinship_array=[avg_gotchi],
                                                num_days=days,
                                                current_altaar=1,
                                                parcel_dim = [32, 64],
                                                max_allowed_altaar=level+1)
                 for level in range(9)],
    }