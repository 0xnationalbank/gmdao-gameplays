import logging

from flask import Flask, make_response, jsonify, request
from flask_cors import CORS, cross_origin
#from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api


import os


app = Flask(__name__) # flask application initialization
cors = CORS(app)

app.config.SWAGGER_UI_DOC_EXPANSION = 'full'


# restplus swagger-ui
api = Api(app, version='1.0', title='Gochiverse gameplay', prefix='/api/v1',
          description='Application to access gochiverse gameplays')




import sys

#ENV = 'DEV'
ENV = 'PROD'



@app.route("/ping")
def hello():
    return jsonify({'msg': "hello"})



# check the header and compare to
@app.before_request
def before_request_func():
    if request.method == 'OPTIONS':
        return jsonify({'message': "in the middleware API"})
    #print("before request >>>>>>>>>>>>>")
    if not (request.path == '/' or 'swagger' in request.path):
        print("handle unauthorised requests here")
        #return make_response(response, 401)
