from flask import make_response, jsonify, request

from src.instance.flask_app import api
from flask_restplus import Resource, fields
from src.namespace import home_page_api
from src.misc.misc_functions import *

import time, random



from random import randrange



class MyParcel:
    level = 1
    dim = (8, 8)
    yield_array = [0]*9
    def __init__(self, level, dim, days, avg_gotchi):
        self.level = level
        self.dim = dim
        yield_dict = compute_yield_dict(days, avg_gotchi)
        self.yield_array = yield_dict[dim]

    def get_next_level_yield(self):
        assert self.level < 8, "9 is the maximum available level"
        return self.yield_array[self.level+1][0], self.yield_array[self.level+1][1]


class MyParcel_1:
    level = 1
    dim = (8, 8)
    num_gotchi = 0
    gotchi_kinship_array = []
    def __init__(self, level, dim, num_gotchi):
        self.level = level
        self.dim = dim
        self.num_gotchi = num_gotchi
        self.gotchi_kinship_array = []



@home_page_api.route('/gameplay_v5')
@home_page_api.param('gotchi_array', 'comma-separated gotchi kinships')
@home_page_api.param('parcel_array', 'comman-separated parcels in order of humble, reasonable, spacious')
@home_page_api.param('days', 'number of play days')
class ClubHomePosts(Resource):
    def get(self):
        """
        returns posts of Clubs
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

        for i in range(parcel_input[0]):
            Parcels.append(MyParcel(0, (8, 8), days, avg_gotchi))
            
        for i in range(parcel_input[1]):
            Parcels.append(MyParcel(0, (16, 16), days, avg_gotchi))
            
        for i in range(parcel_input[2]):
            Parcels.append(MyParcel(0, (32, 64), days, avg_gotchi))


        num_available_gotchis = len(gotchi_kinship_array)
        gotchi_kinship_array.sort(reverse=True)

        while(num_available_gotchis > 0):
            # check which is best among the upgradeable levels
            next_upgradeable_parcel = 0
            max_upgradeable_yield, _ = Parcels[0].get_next_level_yield()
            
            print("new loop")
            print("num_available_gotchis is {}".format(num_available_gotchis))
            
            for i in range(len(Parcels)):
                next_level_yield, level_constructed = Parcels[i].get_next_level_yield()
                print("current level {} --- next level {} --> next yield {}".format(Parcels[i].level, level_constructed, next_level_yield))
                
                if level_constructed < Parcels[i].level:
                    max_upgradeable_yield = -1
                
                elif next_level_yield > max_upgradeable_yield:
                    max_upgradeable_yield = next_level_yield
                    next_upgradeable_parcel = i
            
            
            #print(max_upgradeable_yield)
            
            if max_upgradeable_yield < 0:
                break
            
            
            #upgrade the index thus achieved, and reduce the num available gotchis
            Parcels[next_upgradeable_parcel].level += 1
            new_level = Parcels[next_upgradeable_parcel].level
            
            
            channel_frequency = int(24/CHANNELING_RATE_IN_HOURS[altaar_level])
            extra_available_channeling_slots = int(24/CHANNELING_RATE_IN_HOURS[new_level]) - int(24/CHANNELING_RATE_IN_HOURS[new_level - 1])
            print("extra slots --> {}".format(extra_available_channeling_slots))
            num_available_gotchis -= extra_available_channeling_slots


        result = {}
        for i in range(len(Parcels)):
            if str(Parcels[i].dim) in result:
                result[str(Parcels[i].dim)].append(Parcels[i].level)
            else:
                result[str(Parcels[i].dim)] = [Parcels[i].level]
            print("size {} level constructed {}".format(Parcels[i].dim, Parcels[i].level))

        
        return make_response(jsonify(result), 200)






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
            
            _, parcel.level = gameplay_v3(gotchi_kinship_array=parcel.gotchi_kinship_array,
                        num_days=days,
                        current_altaar=1,
                        parcel_dim = parcel.dim,
                        max_allowed_altaar=9)


        result = {}
        for i in range(len(Parcels)):
            if str(Parcels[i].dim) in result:
                result[str(Parcels[i].dim)].append(Parcels[i].level)
            else:
                result[str(Parcels[i].dim)] = [Parcels[i].level]
            print("size {} level constructed {}".format(Parcels[i].dim, Parcels[i].level))


        return make_response(jsonify(result), 200)