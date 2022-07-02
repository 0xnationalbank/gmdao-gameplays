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




try:
    URL = "https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi-fud%2Caavegotchi-fomo%2Caavegotchi-alpha%2Caavegotchi-kek%2Caavegotchi&vs_currencies=usd"
    result = requests.get(url = URL).json()

    fud_factor = 1.0
    fomo_factor = result['aavegotchi-fomo']['usd']/result['aavegotchi-fud']['usd']
    alpha_factor = result['aavegotchi-alpha']['usd']/result['aavegotchi-fud']['usd']
    kek_factor = result['aavegotchi-kek']['usd']/result['aavegotchi-fud']['usd']
except:
    print("unable to get token factors from the API")
    fud_factor = 1.0
    fomo_factor = 2.0
    alpha_factor = 10.0
    kek_factor = 20.0


class Yield:
    fud = 0
    fomo = 0
    alpha = 0
    kek = 0
    def __init__(self, fud = 0, fomo = 0, alpha = 0, kek = 0):
        self.fud = fud
        self.fomo = fomo
        self.alpha = alpha
        self.kek = kek
        
    
    def add_yield(self, y1):
        self.fud += y1.fud
        self.fomo += y1.fomo
        self.alpha += y1.alpha
        self.kek += y1.kek
        
    def substract_yield(self, y1):
        self.fud -= y1.fud
        self.fomo -= y1.fomo
        self.alpha -= y1.alpha
        self.kek -= y1.kek
        
    def add_yield_by_base_rate(self, base_rate, factor):
        # base rate is a 4 dimensional array
        self.fud += base_rate[0] * factor
        self.fomo += base_rate[1] * factor
        self.alpha += base_rate[2] * factor
        self.kek += base_rate[3] * factor
        
    def get_total_yield_in_fud(self):
        try:
            URL = "https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi-fud%2Caavegotchi-fomo%2Caavegotchi-alpha%2Caavegotchi-kek%2Caavegotchi&vs_currencies=usd"
            result = requests.get(url = URL).json()

            fud_factor = 1.0
            fomo_factor = result['aavegotchi-fomo']['usd']/result['aavegotchi-fud']['usd']
            alpha_factor = result['aavegotchi-alpha']['usd']/result['aavegotchi-fud']['usd']
            kek_factor = result['aavegotchi-kek']['usd']/result['aavegotchi-fud']['usd']
        except:
            print("unable to get token factors from the API")
            fud_factor = 1.0
            fomo_factor = 2.0
            alpha_factor = 10.0
            kek_factor = 20.0
            
        return fud_factor*self.fud + fomo_factor*self.fomo + alpha_factor*self.alpha + kek_factor*self.kek
    
    def diplay(self):
        print("FUD: {}\nFOMO: {}\nALPHA: {}\nKEK: {}".format(self.fud, self.fomo, self.alpha, self.kek))




CHANNELING_RATE_IN_HOURS = {0: float('inf'),
    1:24, 2:18, 3:12, 4:8, 
    5:6, 6:4, 7:3, 8:2, 9:1
}

INCLUDE_SPILLOVER_COMPUTATION = False


altaar_cost_df = pd.read_csv("data/altaar_cost.csv")
altaar_cost_df = altaar_cost_df.replace(',','', regex=True)

altaar_built_time_dict = { altaar_cost_df['Level'][i]: altaar_cost_df['Buid Time (Days) '][i] for i in range(altaar_cost_df.shape[0]) }

altaar_built_cost_dict_in_alchemica = {
    altaar_cost_df['Level'][i]: Yield(fud = int(altaar_cost_df['FUD'][i]),
                                      fomo = int(altaar_cost_df['FOMO'][i]),
                                      alpha = int(altaar_cost_df['ALPHA'][i]),
                                      kek = int(altaar_cost_df['KEK'][i]),
                                     )
    for i in range(altaar_cost_df.shape[0])
}



altaar_built_cost_dict = { altaar_cost_df['Level'][i]: 
                          fud_factor*int(altaar_cost_df['FUD'][i])+
                          fomo_factor*int(altaar_cost_df['FOMO'][i])+
                          alpha_factor*int(altaar_cost_df['ALPHA'][i])+
                          kek_factor*int(altaar_cost_df['KEK'][i]) 
                          for i in range(altaar_cost_df.shape[0]) }


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

yield = yield_from_altaar + yield_from_spillover,

where,

actual_yield = frequency_of_channel x base_rate_yield x channeling_modifier
yield_from_altaar = actual_yield x (1-spillover_rate)
yield_from_spillover = actual_yield x spillover_rate x collection_rate
"""

def get_yield_for_the_day(gotchi_kinship_array, altaar_level, parcel_dim):
    
    yield_obj = Yield()
    
    x, y = parcel_dim
    
    spillover_rate = (50 - (altaar_level-1)*5)/100.0
    
    channeling_modifier_array = sorted([math.sqrt(ele/50) for ele in gotchi_kinship_array], reverse=True) #start by using gotchi's who have more kinship
    
    channel_frequency = int(24/CHANNELING_RATE_IN_HOURS[altaar_level])
    
    total_yield = 0
    for i in range(min(len(gotchi_kinship_array), int(channel_frequency))):
        
        #yield from the altaar
        total_yield += int(channeling_modifier_array[i]*yield_at_base_rate*(1-spillover_rate))
        
        yield_obj.add_yield_by_base_rate(BASE_RATE, channeling_modifier_array[i]*(1-spillover_rate))
        
        if INCLUDE_SPILLOVER_COMPUTATION:
            total_yield += int(channeling_modifier_array[i]*yield_at_base_rate*spillover_rate * spill_collection_rate(x, y))
            yield_obj.add_yield_by_base_rate(BASE_RATE, channeling_modifier_array[i]*spillover_rate * spill_collection_rate(x, y))
    
    return total_yield, yield_obj



"""
TODO: need to implement this function covering all the types of scenarios
1. day will be divided into 2 parts. one with the original altar, 2nd with the upgraded altar
2. gotchi's need to make a choice which altaar to channel, depending on how many channel frequency are available in each
3. preferably gotchi's should channel the upgraded altar
"""
def get_yield_for_the_upgrade_day(gotchi_kinship_array, altaar_level, parcel_dim, pending_built_time):
    # using the same function as of now, will work on this function later
    return get_yield_for_the_day(gotchi_kinship_array, altaar_level, parcel_dim)



def future_yield_by_current_altaar(gotchi_kinship_array, altaar_level, parcel_dim, num_days):
    
    gotchi_array = gotchi_kinship_array.copy()
    
    yield_till_now = 0
    for i in range(num_days):
        yield_till_now += get_yield_for_the_day(gotchi_array, altaar_level, parcel_dim)[0]
        gotchi_array[:] = map(lambda x: x+2, gotchi_array) # gotchi kinships increase by 2 everyday
        
    return yield_till_now



def get_breakeven_time(Parcels, num_days):
    
    daywise_profit_yield_array = [0]*num_days
    
    
    
    
    
    for parcel in Parcels:
        total_yield_till_now = 0
        profit_yield_till_now = 0
        yield_obj = Yield()
        profit_yield_obj = Yield()
        
        parcel_dim = parcel.dim
        target_altaar_level = parcel.altaar_level
        gotchi_kinship_array = parcel.gotchi_kinship_array
                
        current_altaar = 1
        pending_built_time_for_next_altaar = math.inf if current_altaar >= target_altaar_level else altaar_built_time_dict[current_altaar+1]
        
        for i in range(num_days):
            
            if current_altaar > target_altaar_level:
                break

            if pending_built_time_for_next_altaar <=1:
                
                t1 = get_yield_for_the_upgrade_day(gotchi_kinship_array, current_altaar, parcel_dim, pending_built_time_for_next_altaar)
                
                yield_obj.add_yield(t1[1])
                profit_yield_obj.add_yield(t1[1])
                profit_yield_obj.substract_yield(altaar_built_cost_dict_in_alchemica[current_altaar+1])
                
                altaar_built_cost_dict_in_alchemica
                
                total_yield_till_now += t1[0]
                profit_yield_till_now += t1[0] - altaar_built_cost_dict[current_altaar+1] 

                if current_altaar == target_altaar_level-1:
                    current_altaar = current_altaar + 1
                    pending_built_time_for_next_altaar = math.inf
                elif current_altaar == target_altaar_level:
                    pending_built_time_for_next_altaar = math.inf
                else:
                    current_altaar = current_altaar + 1
                    pending_built_time_for_next_altaar = altaar_built_time_dict[current_altaar+1]

            else:
                t1 = get_yield_for_the_day(gotchi_kinship_array, current_altaar, parcel_dim)

                yield_obj.add_yield(t1[1])
                profit_yield_obj.add_yield(t1[1])
                
                total_yield_till_now += t1[0]
                profit_yield_till_now += t1[0]
                
                pending_built_time_for_next_altaar -= 1

                            

            daywise_profit_yield_array[i] += profit_yield_till_now
            gotchi_kinship_array = [ele+2 for ele in gotchi_kinship_array]
        
            #print("day {}, current level {}, pending time {}, current total yield {}".format(i+1, current_altaar, pending_built_time_for_next_altaar, total_yield_till_now))
    
    

#     print("----------------------------------------")
#     print("total yield --> {}, profit yield --> {}".format(total_yield_till_now, profit_yield_till_now))
#     print("\n")
#     yield_obj.diplay()
#     print(yield_obj.get_total_yield_in_fud())

#     print("\n")
#     profit_yield_obj.diplay()
#     print(profit_yield_obj.get_total_yield_in_fud())
    
    
    last_neg = 0
    for i, ele in enumerate(daywise_profit_yield_array):
        if ele<=0:
            last_neg = i
            
    
    #print(daywise_total_yield_array)

    if last_neg == num_days-1:
        return -1, yield_obj, profit_yield_obj
    
    return last_neg, yield_obj, profit_yield_obj




"""
Given (a) number of days (b) maximum allowed altaar built,
this function computes the maximum yield possible, and till what level should the altaar be upgraded
"""
def gameplay_v3(gotchi_kinship_array, num_days, current_altaar, parcel_dim, max_allowed_altaar):

    pending_built_time_for_next_altaar = math.inf if current_altaar >= max_allowed_altaar else altaar_built_time_dict[current_altaar+1]
    
    total_yield_till_now = 0
    
    max_expected_yield = 0
    max_yield_level = 0
    
    for i in range(num_days):
                
        if pending_built_time_for_next_altaar <=1: #altaar can be made current day
            
            total_yield_till_now += get_yield_for_the_upgrade_day(gotchi_kinship_array, current_altaar, parcel_dim, pending_built_time_for_next_altaar)[0]
            
            #print("kinship array {}, altaar level {} parcel dim {} pendinng time {} total yield {}".format(gotchi_kinship_array, current_altaar, parcel_dim, pending_built_time_for_next_altaar, get_yield_for_the_upgrade_day(gotchi_kinship_array, current_altaar, parcel_dim, pending_built_time_for_next_altaar)))

            total_yield_till_now -= altaar_built_cost_dict[current_altaar+1]  #reducing the total cost for building the altaar
            #print("came here {} {}".format(altaar_built_cost_dict[current_altaar+1], total_yield_till_now))
            
            if current_altaar == max_allowed_altaar-1:
                current_altaar = current_altaar + 1
                pending_built_time_for_next_altaar = math.inf
            elif current_altaar == max_allowed_altaar:
                pending_built_time_for_next_altaar = math.inf
            else:
                current_altaar = current_altaar + 1
                pending_built_time_for_next_altaar = altaar_built_time_dict[current_altaar+1]

        else:
            total_yield_till_now += get_yield_for_the_day(gotchi_kinship_array, current_altaar, parcel_dim)[0]
            pending_built_time_for_next_altaar -= 1
            
            
        #print("day {}, current level {}, pending time {}, current total yield {}".format(i+1, current_altaar, pending_built_time_for_next_altaar, total_yield_till_now))
        
        future_yield = future_yield_by_current_altaar(gotchi_kinship_array, current_altaar, parcel_dim, num_days-i-1)
                
        if total_yield_till_now + future_yield > max_expected_yield:
            max_expected_yield = total_yield_till_now + future_yield
            max_yield_level = current_altaar
        
        gotchi_kinship_array = [ele+2 for ele in gotchi_kinship_array]

    return max_expected_yield, max_yield_level





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