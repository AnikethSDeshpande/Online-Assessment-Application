# Author: Aniketh S Deshpande
# API-name: Login
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from random import randint
from hashlib import sha1
from config import get_ip

ip_address = get_ip()

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)


# QuestionBankListAPI
class QuestionBankList(Resource):
    def get(self):
        mongo_obj = list(mongo.db.qbanks.find({}) )
        qb_names = []
        for qb_name in mongo_obj:
            qb_names.append(qb_name['name'])

        return {"qb_names": qb_names}



# resources routing
api.add_resource(QuestionBankList, '/question_bank_list')  



# ipaddress loaded dynamically
if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5058)
