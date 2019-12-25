# Author: Aniketh S Deshpande
# API-name: ShowQuiz-API
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from random import randint, shuffle
from hashlib import sha384
from config import get_ip


ip_address = get_ip()

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)

class Information(Resource):
    def post(self):
        obj = request.get_json(force=True)
        passKey = sha384(obj['passkey'].encode())
        
        if (passKey.hexdigest() == 'ed3625790b58dc0c72ed2dfca8e9776ca2500e095666818920c436acd0d1d31f3831112001ef3241b75d6c83dfe10b9b' or passKey.hexdigest()=='7a5296c393b2d50ab03bd8c0365024e7f7b0fee1fee46e0016cfa40dfb822640cdcd73c7ff15c1d0514aa3acec1735af') and obj['requirement']=='students':
            mongo_obj = list(mongo.db.student_details.find() )
            return {
                'students': str(mongo_obj)
            }
        
        if (passKey.hexdigest()=='7a5296c393b2d50ab03bd8c0365024e7f7b0fee1fee46e0016cfa40dfb822640cdcd73c7ff15c1d0514aa3acec1735af' or passKey.hexdigest() == 'ed3625790b58dc0c72ed2dfca8e9776ca2500e095666818920c436acd0d1d31f3831112001ef3241b75d6c83dfe10b9b') and obj['requirement']=='faculty':
            mongo_obj = list(mongo.db.login.find() )
            return {
                'faculty': str(mongo_obj)
            }
        return {'passKey_sha384': passKey.hexdigest()}

# resources routing
api.add_resource(Information, '/get_all_details')


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5057)

