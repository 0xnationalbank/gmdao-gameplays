from flask import make_response, jsonify, request

from src.instance.flask_app import api
from flask_restplus import Resource, fields
from src.namespace import harvesters_api
from src.misc.misc_functions_harvesters import *

import time, random



from random import randrange



class MyParcel_3:
    dim = None
    max_allowed_harvestors = [0,0,0,0]
    tag = None
    alchemica_content = None
    
    
    def __init__(self, dim):
        self.dim = dim
        
        if dim == (8,8):
            self.max_allowed_harvestor = [1,1,1,1]
            self.tag = 'humble'
            self.alchemica_content = [7077, 3539, 1769, 708]
        elif dim == (16,16):
            self.max_allowed_harvestor = [4,4,4,4]
            self.tag = 'reasonable'
            self.alchemica_content = [28308, 14154, 7077, 2831]
        elif dim == (32,64):
            self.max_allowed_harvestor = [32,32,32,32]
            self.tag = 'spacious'
            self.alchemica_content = [226465, 113233, 56616, 22647]
        
    def max_allowed_harvestors_for_alchemica(self, alchemica_type):
        if alchemica_type == 'FUD':
            return self.max_allowed_harvestor[0]
        elif alchemica_type == 'FOMO':
            return self.max_allowed_harvestor[1]
        elif alchemica_type == 'ALPHA':
            return self.max_allowed_harvestor[2]
        elif alchemica_type == 'KEK':
            return self.max_allowed_harvestor[3]
        else:
            return 0
        
    def get_alchemica_content(self, alchemica_type):
        if alchemica_type == 'FUD':
            return self.alchemica_content[0]
        elif alchemica_type == 'FOMO':
            return self.alchemica_content[1]
        elif alchemica_type == 'ALPHA':
            return self.alchemica_content[2]
        elif alchemica_type == 'KEK':
            return self.alchemica_content[3]
        else:
            return 0
        
    def print_parcel_info(self):
        print("parcel dim {}".format(self.dim))
        print("alchemica content ", self.alchemica_content)

    


@harvesters_api.route('/harvester_v1')
@harvesters_api.param('parcel_array', 'comman-separated parcels in order of humble, reasonable, spacious')
@harvesters_api.param('days', 'number of play days')
class HarvesterV1(Resource):
    def get(self):
        """
        This gameplay 
        :return:

            {
                "todo"
            }
        """

        parcel_array = request.args.get('parcel_array')
        T = int(request.args.get('days'))

        parcel_input = list(map(int, parcel_array.split(",")))


        Parcels = []

        for i in range(parcel_input[2]):
            Parcels.append(MyParcel_3((32, 64)))

        for i in range(parcel_input[1]):
            Parcels.append(MyParcel_3((16, 16)))

        for i in range(parcel_input[0]):
            Parcels.append(MyParcel_3((8, 8)))
        



        result = []
        for parcel in Parcels:
                
            pc = {}
            pc['parcel_size'] = " ".join([str(ele) for ele in list(parcel.dim)])
            
            pc['installations'] = {}
            total_profit_in_fud = 0
            
            #parcel.print_parcel_info()
            
            for alchemica in ['FUD', 'FOMO', 'ALPHA', 'KEK']:
                
                #print(parcel.print_parcel_info(), alchemica)
                
                parcel_alchemica_content = parcel.get_alchemica_content(alchemica)
                
                harvesters_array, reservoirs_array, profit = compute_harvestor_reservoir_for_parcel_alchemica(parcel, alchemica, T, parcel_alchemica_content)

                    
                harvesters_array = list(filter(lambda num: num != 0, harvesters_array)) #removing extra zeros from harvester array
                
                #print("harvesters_array {}, reservoirs_array {}, profit_yield_in_fud {}".format(harvesters_array, reservoirs_array, int(profit)))

                if profit > 0:
                    pc['installations'][alchemica + " " + "harvester"] = " ".join([str(ele) for ele in list(harvesters_array)])
                    pc['installations'][alchemica + " " + "reservoir"] = " ".join([str(ele) for ele in list(reservoirs_array)])
                    total_profit_in_fud += profit 
                
                
                #print("...........................................")
                #print("alchemica --> {}, profit --> {}".format(alchemica, profit))

            
            pc["profit_yield_in_fud"] = int(total_profit_in_fud)

            result.append(pc)
                        
        return make_response(jsonify({
            "result": result
        }), 200)