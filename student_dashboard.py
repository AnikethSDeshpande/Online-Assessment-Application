# Author: Aniketh S Deshpande
# API-name: StudentDashboard
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from random import randint
from hashlib import sha1
from config import get_ip
from show_quiz import SudentPassKeyAuth

ip_address = get_ip()

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)

# Student Dashboard API
class StudentDashboard(Resource):
    def post(self):
        obj = request.get_json(force=True)

        response_given = list(mongo.db.responses.aggregate([
            {
                '$match': {
                    'email_id': obj['email_id']
                }
            },

            {
                '$lookup': {
                    'from': 'items',
                    'localField': 'item_password',
                    'foreignField': 'item_password',
                    'as': 'lookup'
                }
            },

            {
                '$project': {
                    'lookup': {
                        'subject': 1,
                        'ia': 1,
                        'semester': 1,
                        'questions': 1,
                        'positive_marks': 1,
                        'negative_marks': 1,
                        'gate': 1
                    },
                    'student_response': 1,
                    'score': 1,
                    'item_password': 1
                }
            }
        ])
        )

        response_given_list = []

        for response in response_given:
            response_given_list.append({
                'subject': response['lookup'][0]['subject'],
                'ia': response['lookup'][0]['ia'],
                'semester': response['lookup'][0]['semester'],
                'questions': response['lookup'][0]['questions'],
                'positive_marks': response['lookup'][0]['positive_marks'],
                'negative_marks': response['lookup'][0]['negative_marks'],
                'student_response': response['student_response'],
                'score': response['score'],
                'gate': response['lookup'][0]['gate']
            })

        if len(response_given_list)>0:
            return {
                'status': 'success',
                'response_list': response_given_list
            }
        else:
            return {
                'status': 'failed',
                'error': 'NO_RESPONSES'
            }


# resources routing
api.add_resource(StudentDashboard, '/student_dashboard')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5055)
