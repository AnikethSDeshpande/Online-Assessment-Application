# Author: Aniketh S Deshpande
# API-name: Login
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from config import get_ip

ip_address = get_ip()

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)



class FacultyContributeQB(Resource):
    def post(self):
        obj = request.get_json(force=True)
        qb_name = obj['qb_name']
        questions = obj['questions']

        mongo_obj = dict(mongo.db.qbanks.update(
            {
                "name": qb_name
            },

            {
                "$set": {
                    "questions": questions
                }
            }
        ))

        if mongo_obj['nModified'] == 1:
            return {
                'status': 'success'
            }
    

class GetQBQuestions(Resource):
    def post(self):
        obj = request.get_json(force=True)

        qb_name = obj['qb_name']

        mongo_obj = list(mongo.db.qbanks.find({
            "name": qb_name
        }))

        return {
            'status': 'success',
            'description': mongo_obj[0]['description'],
            'questions': mongo_obj[0]['questions']
        }




# resources routing
api.add_resource(FacultyContributeQB, '/insert_update_qb')  
api.add_resource(GetQBQuestions, '/get_qb_questions')  


# ipaddress loaded dynamically
if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5059)
