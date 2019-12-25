# Author: Aniketh S Deshpande
# API-name: FacultyDashboard
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

# Faculty Dashboard API
class FacultyDashboard(Resource):
    def item_list(self, email_id):
        items = list(mongo.db.items.find(
            {
                'email_id': email_id
            }
        ))
        
        if not items:
            return []

        item_list = []
        for item in items:
            item_list.append({
                'subject': item['subject'],
                'ia': item['ia'],
                'semester': item['semester'],
                'item_password': item['item_password'],
                'gate': item['gate']
            })

        return item_list

    def post(self):
        obj = request.get_json(force=True)
        email_id = obj['email_id']
        
        return {
            'status': 'success',
            'items': self.item_list(email_id)
        }


# ResponsesDashboard

class ResponsesDashboard(Resource):
    def post(self):
        obj = request.get_json(force=True)
    
        # code to get the question paper of the corresponding item_password
        ext_obj = SudentPassKeyAuth()
        question_paper = ext_obj.format_questions(obj['item_password'], '_escape_')


        # code to get the responses wrt to the given item_password
        responses = list(mongo.db.responses.aggregate([
            {
                '$match': {
                    'item_password': obj['item_password']
                }
            },

            {
                '$lookup': {
                    'from': 'student_details',
                    'localField': 'email_id',
                    'foreignField': 'email_id',
                    'as': 'lookup'
                }
            },

            {
                '$project': {
                    'email_id':1,
                    'student_response': 1,
                    'score': 1,
                    'lookup': {'username': 1, 'details': {'usn': 1}}
		        }
            },

            {
                '$sort': {
                    'score': -1
                }
            }

        ])
        
        )
        
        response_list = []

        for response in responses:
            response_list.append({
                'username': response['lookup'][0]['username'],
                'score': response['score'],
                'usn': response['lookup'][0]['details']['usn'],
                'student_response': response['student_response'],
                'email_id': response['email_id']
            })

        if len(responses)>0:
            stats = list(mongo.db.responses.aggregate([
                {
                    '$match': {
                        'item_password': obj['item_password']
                    }
                },
                {
                    '$group': {
                        '_id': 'null',
                        'average_score': {
                            '$avg': '$score'
                        }
                    }
                }
            ])
            )

            return {
                'status': 'success',
                'average': stats[0]['average_score'],
                'responses_count': len(response_list),
                'response_list': response_list,
                'question_paper': question_paper,
                'item_password': obj['item_password']
            }
        
        else:
            return {
                'status': 'failed',
                'error': 'NO_RESPONSES'
            }


# ChangeItemStatus

class ChangeItemStatus(Resource):
    def post(self):
        obj = request.get_json(force=True)
        item_password = obj['item_password']
        gate = obj['gate']

        result = mongo.db.items.update(
            {
                'item_password': item_password
            },

            {
                '$set': {
                    'gate': gate
                }
            }
        )
        
        if result['nModified'] == 1:
            return {
                'status': 'success',
                'gate': gate
            }
        else:
            return {
                'status': 'failed',
            }


class DeleteResponse(Resource):
    def post(self):
        obj = request.get_json(force=True)
        item_password = obj['item_password']
        email_ids = obj['email_ids']

        for email_id in email_ids:
            result = mongo.db.responses.remove(
                {
                    'item_password': item_password,
                    'email_id': email_id
                }
            )
        
        if result:
            return {
                'status': 'success',
                'item_password': item_password,
            }


# resources routing
api.add_resource(FacultyDashboard, '/faculty_dashboard')
api.add_resource(ResponsesDashboard, '/get_response_list')
api.add_resource(ChangeItemStatus, '/change_item_gate')
api.add_resource(DeleteResponse, '/delete_response_')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5054)
