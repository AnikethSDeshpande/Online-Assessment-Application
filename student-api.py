# Author: Aniketh S Deshpande
# API-name: Student-API
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from random import randint
from hashlib import sha1

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)


# Get-Item-API
class GetItems(Resource):

    def get(self):
        # obj = request.get_json(force=True)
        items = mongo.db.items.find()   
        items_ = [item['item_name'] for item in items]
        
        return {
            'items': items_
            }


class StudentRegistration(Resource):
    def post(self):
        obj = request.get_json(force=True)

        item_name = obj['item_name']
        student_name = obj['student_name']
        student_password = obj['student_password']
        
        result = mongo.db.items.update(
            {'item_name': item_name},
            {
                '$push': {
                    'registrations': {
                        'student_name': student_name,
                        'student_password': student_password
                    }
                }
            }
        )
        
        return {
            "status": "success",
            "student_name": student_name 
            }


# resources routing
api.add_resource(GetItems, '/get_items')
api.add_resource(StudentRegistration, '/student_registration')

if __name__ == '__main__':
    app.run(debug=True, host='10.10.5.240', port=5052)

