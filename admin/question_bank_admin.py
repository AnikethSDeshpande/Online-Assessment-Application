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
            qb_names.append({
                "name": qb_name['name'],
                "description": qb_name['description'],
                'no_of_questions': len(qb_name['questions'])
            })

        return {"qb_names": qb_names}

class NewQuestionBank(Resource):

    def post(self):
        obj = request.get_json(force=True)

        name = obj['qb_name']
        description = obj['description']

        qb_list = QuestionBankList()

        qbs = qb_list.get()

        print(name, qbs)
        arr = qbs['qb_names']
        exist = False
        for x in arr:
            if x['name'] == name:
                return {
                    'status': 'failed',
                    'error': 'qb_name_repeat_error'
                }



        mongo_obj = mongo.db.qbanks.insert({
            "name": name,
            "description": str(description),
            "questions": []
        })
        
        new_list = qb_list.get()

        if mongo_obj:
            return {
                'status': 'success',
                'new_list': new_list['qb_names']
            }

        return {
            'status': 'failed',
            'error': 'one or more fields empty'
        }





# resources routing
api.add_resource(QuestionBankList, '/question_bank_list')  
api.add_resource(NewQuestionBank, '/new_qb')  




# ipaddress loaded dynamically
if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5058)
