from flask import make_response, jsonify, request

from src.instance.flask_app import api
from flask_restplus import Resource, fields
from src.namespace import home_page_api
from src.misc.misc_functions import *

import time, random



from random import randrange



class MyParcel:
    altaar_level = 0
    dim = (8, 8)
    yield_array = [0]*9
    gotchi_kinship_array = []
    def __init__(self, altaar_level, dim, days, avg_gotchi):
        self.altaar_level = altaar_level
        self.dim = dim
        yield_dict = compute_yield_dict(days, avg_gotchi)
        self.yield_array = yield_dict[dim]
        self.gotchi_kinship_array = []

    def get_next_level_yield(self):
        assert self.altaar_level < 8, "9 is the maximum available level"
        return self.yield_array[self.altaar_level+1][0], self.yield_array[self.altaar_level+1][1]


class MyParcel_1:
    altaar_level = 1
    reservior_level = 0
    dim = (8, 8)
    num_gotchi = 0
    gotchi_kinship_array = [] #this is the arrays which suggests what gotchis have been assigned to collect from this parcel
    
    def __init__(self, altaar_level, dim, num_gotchi):
        self.altaar_level = altaar_level
        self.dim = dim
        self.num_gotchi = num_gotchi
        self.gotchi_kinship_array = []
        
    def reset_parcel(self):
        #reset everything except the size
        self.altaar_level = 0
        self.num_gotchi = 0
        self.gotchi_kinship_array = []
        
        
    def print_parcel_info(self):
        print("parcel size {} --> parcel level {} --> parcel gotchi {}".format(self.dim, self.altaar_level, self.num_gotchi))
        channel_frequency = int(24/CHANNELING_RATE_IN_HOURS[self.altaar_level])
        print("channel capacity of level {} num open slots {}".format(channel_frequency, channel_frequency - self.num_gotchi))





@home_page_api.route('/gameplay_v5')
@home_page_api.param('gotchi_array', 'comma-separated gotchi kinships')
@home_page_api.param('parcel_array', 'comman-separated parcels in order of humble, reasonable, spacious')
@home_page_api.param('days', 'number of play days')
class ClubHomePosts(Resource):
    def get(self):
        """
        returns optimal levels for a givennumber of days
        :return:

            {
                "(16, 16)": [1,1],
                "(32, 64)": [2,2],
                "(8, 8)": [1,1]
            }
        """

        gotchi_array = request.args.get('gotchi_array')
        parcel_array = request.args.get('parcel_array')
        days = int(request.args.get('days'))

        parcel_input = list(map(int, parcel_array.split(",")))
        
        gotchi_kinship_array = list(map(int, gotchi_array.split(",")))


        avg_gotchi = sum(gotchi_kinship_array)/len(gotchi_kinship_array)
        
        Parcels = []

        for i in range(parcel_input[2]):
            Parcels.append(MyParcel(0, (32, 64), days, avg_gotchi))

        for i in range(parcel_input[1]):
            Parcels.append(MyParcel(0, (16, 16), days, avg_gotchi))

        for i in range(parcel_input[0]):
            Parcels.append(MyParcel(0, (8, 8), days, avg_gotchi))


        num_available_gotchis = len(gotchi_kinship_array)
        gotchi_kinship_array.sort(reverse=True)

        while(num_available_gotchis > 0):
            # check which is best among the upgradeable levels
            next_upgradeable_parcel = 0
            max_upgradeable_yield, _ = Parcels[0].get_next_level_yield()

            #print("new loop")
            #print("num_available_gotchis is {}".format(num_available_gotchis))

            for i in range(len(Parcels)):
                next_level_yield, level_constructed = Parcels[i].get_next_level_yield()
                #print("current level {} --- next level {} --> next yield {}".format(Parcels[i].altaar_level, level_constructed, next_level_yield))

                if level_constructed < Parcels[i].altaar_level:
                    max_upgradeable_yield = -1

                elif next_level_yield > max_upgradeable_yield:
                    max_upgradeable_yield = next_level_yield
                    next_upgradeable_parcel = i


            #print(max_upgradeable_yield)

            if max_upgradeable_yield < 0:
                break


            #upgrade the index thus achieved, and reduce the num available gotchis
            Parcels[next_upgradeable_parcel].altaar_level += 1
            new_level = Parcels[next_upgradeable_parcel].altaar_level


            #channel_frequency = int(24/CHANNELING_RATE_IN_HOURS[new_level])
            extra_available_channeling_slots = int(24/CHANNELING_RATE_IN_HOURS[new_level]) - int(24/CHANNELING_RATE_IN_HOURS[new_level - 1])
            #print("extra slots --> {}".format(extra_available_channeling_slots))
            num_available_gotchis -= extra_available_channeling_slots
            
            for _ in range(extra_available_channeling_slots):
                Parcels[next_upgradeable_parcel].gotchi_kinship_array.append(gotchi_kinship_array[0])
                gotchi_kinship_array.pop(0)


        result = []
        for parcel in Parcels:
            pc = {}
            pc['parcel_size'] =  " ".join([str(ele) for ele in list(parcel.dim)])
            pc['altaar_level'] = parcel.altaar_level
            pc['gotchis'] = ",".join([str(item) for item in parcel.gotchi_kinship_array])
            result.append(pc)


        breakeven_time, ty, py = get_breakeven_time(Parcels, days)

        
        return make_response(jsonify({
            "result": result,
            "breakeven_time": breakeven_time,
            "total_yield_in_fud": int(ty.get_total_yield_in_fud()),
            "total_yield": {
                "FUD": int(ty.fud),
                "FOMO": int(ty.fomo),
                "ALPHA": int(ty.alpha),
                "KEK": int(ty.kek)
            },
            "profit_yield_in_fud": int(py.get_total_yield_in_fud()),
            "profit_yield": {
                "FUD": int(py.fud),
                "FOMO": int(py.fomo),
                "ALPHA": int(py.alpha),
                "KEK": int(py.kek)
            }
        }), 200)






@home_page_api.route('/gameplay_v7')
@home_page_api.param('gotchi_array', 'comma-separated gotchi kinships')
@home_page_api.param('parcel_array', 'comman-separated parcels in order of humble, reasonable, spacious')
@home_page_api.param('days', 'number of play days')
class ClubHomePosts1(Resource):
    def get(self):
        """
        This gameplay is used when you want to distribute uniformly your gotchis among your parcels
        :return:

            {
                "(16, 16)": [1,1],
                "(32, 64)": [2,2],
                "(8, 8)": [1,1]
            }
        """

        gotchi_array = request.args.get('gotchi_array')
        parcel_array = request.args.get('parcel_array')
        days = int(request.args.get('days'))

        parcel_input = list(map(int, parcel_array.split(",")))
        
        gotchi_kinship_array = list(map(int, gotchi_array.split(",")))


        total_parcels = sum(parcel_input)
        total_gotchis = len(gotchi_kinship_array)

        Parcels = []

        for i in range(parcel_input[2]):
            Parcels.append(MyParcel_1(0, (32, 64), 0))

        for i in range(parcel_input[1]):
            Parcels.append(MyParcel_1(0, (16, 16), 0))
            
        for i in range(parcel_input[0]):
            Parcels.append(MyParcel_1(0, (8, 8), 0))

        gotchi_kinship_array.sort(reverse=True)

        temp = total_gotchis

        while temp > 0:
            for parcel in Parcels:
                parcel.num_gotchi += 1
                temp -= 1
                
                if temp == 0:
                    break

        
        counter = 0
        for parcel in Parcels:
            for i in range(parcel.num_gotchi):
                parcel.gotchi_kinship_array.append(gotchi_kinship_array[counter])
                counter +=1 


        for parcel in Parcels:
            #print("dim {} --> num gotchi {} --> {}".format(parcel.dim, parcel.num_gotchi, parcel.gotchi_kinship_array))
            
            _, parcel.altaar_level = gameplay_v3(gotchi_kinship_array=parcel.gotchi_kinship_array,
                        num_days=days,
                        current_altaar=1,
                        parcel_dim = parcel.dim,
                        max_allowed_altaar=9)

        for parcel in Parcels:
            parcel.print_parcel_info()
        ########### post processing of the results ##################################
        i = 0
        j = len(Parcels)-1
        final_channel_freq = max([parcel.num_gotchi for parcel in Parcels])

        while(i < j):

            if final_channel_freq - Parcels[i].num_gotchi  <=0:
                i += 1
                continue
            
            while Parcels[j].num_gotchi > 0 and Parcels[i].num_gotchi < final_channel_freq:
                gotchi = Parcels[j].gotchi_kinship_array.pop(0)
                Parcels[j].num_gotchi -= 1
                Parcels[i].gotchi_kinship_array.append(gotchi)
                Parcels[i].num_gotchi += 1
            
            if Parcels[j].num_gotchi == 0:
                #Parcels.pop(j)
                Parcels[j].altaar_level = 0
                j -= 1
                
            if Parcels[i].num_gotchi == final_channel_freq:
                i += 1
        ########## post processing ends here ############################################
        for parcel in Parcels:
            parcel.print_parcel_info()


        result = []
        for parcel in Parcels:
            pc = {}
            pc['parcel_size'] = " ".join([str(ele) for ele in list(parcel.dim)])
            pc['altaar_level'] = parcel.altaar_level
            pc['gotchis'] = ",".join([str(item) for item in parcel.gotchi_kinship_array])
            result.append(pc)


        breakeven_time, ty, py = get_breakeven_time(Parcels, days)

        
        return make_response(jsonify({
            "result": result,
            "breakeven_time": breakeven_time,
            "total_yield_in_fud": int(ty.get_total_yield_in_fud()),
            "total_yield": {
                "FUD": int(ty.fud),
                "FOMO": int(ty.fomo),
                "ALPHA": int(ty.alpha),
                "KEK": int(ty.kek)
            },
            "profit_yield_in_fud": int(py.get_total_yield_in_fud()),
            "profit_yield": {
                "FUD": int(py.fud),
                "FOMO": int(py.fomo),
                "ALPHA": int(py.alpha),
                "KEK": int(py.kek)
            }
        }), 200)

        #return make_response(jsonify(result), 200)


