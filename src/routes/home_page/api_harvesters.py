from flask import make_response, jsonify, request

from src.instance.flask_app import api
from flask_restplus import Resource, fields, reqparse
from src.namespace import harvesters_api
from src.misc.misc_functions_harvesters import *

import time, random



from random import randrange



class MyParcel_3:
    dim = None
    max_allowed_harvestors = [0,0,0,0]
    tag = None
    alchemica_content = None
    
    
    def __init__(self, dim, alchemica_content=None):
        self.dim = dim
        
        if dim == (8,8):
            self.max_allowed_harvestor = [1,1,1,1]
            self.tag = 'humble'
            self.alchemica_content = [7077, 3539, 1769, 708] if alchemica_content is None else alchemica_content
        elif dim == (16,16):
            self.max_allowed_harvestor = [4,4,4,4]
            self.tag = 'reasonable'
            self.alchemica_content = [28308, 14154, 7077, 2831] if alchemica_content is None else alchemica_content
        elif dim == (32,64):
            self.max_allowed_harvestor = [32,32,32,32]
            self.tag = 'spacious'
            self.alchemica_content = [226465, 113233, 56616, 22647] if alchemica_content is None else alchemica_content
        
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
        
    def update_alchemica_content(self, new_count, alchemica_type):
        if alchemica_type == 'FUD':
            self.alchemica_content[0] = new_count
        elif alchemica_type == 'FOMO':
            self.alchemica_content[1] = new_count
        elif alchemica_type == 'ALPHA':
            self.alchemica_content[2] = new_count
        elif alchemica_type == 'KEK':
            self.alchemica_content[3] = new_count
        else:
            print("invalid")
        
    def get_all_alchemica_content(self):
        return self.alchemica_content
        
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





parser = reqparse.RequestParser()
parser.add_argument('parcel_type', type=str, required=True, choices=("humble", "reasonable", "spacious"))


@harvesters_api.route('/relative_margin_parcel_alchemica')
@harvesters_api.param('alchemica_array', 'comman-separated alchemica distribution of a parcel')
@harvesters_api.expect(parser)
class MostProfitable(Resource):
    def get(self):
        """
        This gameplay 
        :return:

            {
                "todo"
            }
        """

        input_al = request.args.get('alchemica_array')
        parcel_tag = request.args.get('parcel_type')

        input_al = list(map(int, input_al.split(",")))


        avg_alchemica_per_parcel = avg_alchemica_per_parcel_dict[parcel_tag]
    
        avg_al = [avg_alchemica_per_parcel['FUD'], avg_alchemica_per_parcel['FOMO'],
                avg_alchemica_per_parcel['ALPHA'], avg_alchemica_per_parcel['KEK']]
        
        max_till_now = (input_al[0] - avg_al[0])*100/avg_al[0]
        max_tag = 'FUD'
        
        relative_margin_dict = {}
        for alchemica, x, y in zip(['FUD', 'FOMO', 'ALPHA', 'KEK'], input_al, avg_al):
            margin = (x-y)*100/y
            relative_margin_dict[alchemica] = round(margin,2)
            
        
        return make_response(jsonify({
            "margins": relative_margin_dict
        }), 200)
        
        

@harvesters_api.route('/harvester_v2')
@harvesters_api.param('alchemica_array', 'comman-separated alchemica distribution of a parcel')
@harvesters_api.param('days', 'number of play days')
@harvesters_api.expect(parser)
class HarvesterV1(Resource):
    def get(self):
        """
        This gameplay 
        :return:

            {
                "todo"
            }
        """

        T = int(request.args.get('days'))
        input_al = request.args.get('alchemica_array')
        parcel_tag = request.args.get('parcel_type')
        
        input_al = list(map(int, input_al.split(",")))

        
        parcel = None    

        if parcel_tag == 'spacious':
            parcel = MyParcel_3((32, 64), input_al)
        elif parcel_tag == 'reasonable':
            parcel = MyParcel_3((16, 16), input_al)
        elif parcel_tag == 'humble':
            parcel = MyParcel_3((8, 8), input_al)
            
               
        
        result = []
        while True:
            pc = {}
            all_alchemica_content = parcel.get_all_alchemica_content()
            if sum(all_alchemica_content) == 0:
                break
            #print("alchemica_content_of_parcel -- {}".format(all_alchemica_content))
            
            mpa = most_profitable_alchemica(all_alchemica_content, 'humble')
            max_alchemica_type = max(mpa, key= lambda x: mpa[x])
            #print("most profitable alchemica -- {}".format(max_alchemica_type))

            parcel_alchemica_content = parcel.get_alchemica_content(max_alchemica_type)
            
            optimized_harvestors_array, optimized_reservoirs_array, optimized_profit = compute_harvestor_reservoir_for_parcel_alchemica(parcel, max_alchemica_type, T, parcel_alchemica_content)

            if sum(optimized_harvestors_array) == 0: #break when there is no more harvestor to build
                break
            
            if optimized_profit < 0:
                break
            #print("harvestor to build -- {}".format(optimized_harvestors_array))
            #print("reservoir to build -- {}".format(optimized_reservoirs_array))
            #print("profit made -- {}".format(optimized_profit))
                
            pc['harvestor'] = " ".join([str(ele) for ele in list(filter(lambda num: num != 0, optimized_harvestors_array))])
            pc['reservoir'] = " ".join([str(ele) for ele in optimized_reservoirs_array])
            pc['alchemica_type'] = max_alchemica_type
            
            result.append(pc)
            
            time_spent = time_spent_in_construction(optimized_harvestors_array, optimized_reservoirs_array, max_alchemica_type, 1)
            
            extracted_alchemica_amount = total_alchemica_extracted(optimized_harvestors_array, optimized_reservoirs_array, max_alchemica_type, T, 1)
            #print("time spent in constrution -- {}, extracted alchemica amount -- {}".format(time_spent, extracted_alchemica_amount))

            
            remaining_alchemica = max(0, parcel_alchemica_content - extracted_alchemica_amount)
            parcel.update_alchemica_content(remaining_alchemica, max_alchemica_type)

            T -= time_spent
            #print("remaining time -- {}\n\n".format(T))
            

                        
        return make_response(jsonify({
            "result": result
        }), 200)

