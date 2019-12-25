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

# ShowItemDetails

class ShowItemDetails(Resource):
    def post(self):
        obj = request.get_json(force=True)

        errors = []

        result = list(mongo.db.items.find(
            {
                'item_password': obj['item_password']
            }
        ))

        if result[0]['gate'] != '__close__':
            errors.append('GATE_OPEN_ERR')

        responses = list(mongo.db.responses.find(
            {
                'item_password': obj['item_password']
            }
        ))

        if len(responses) != 0:
            errors.append('RESPONSES_GIVEN_ERR')


        if result:
            return {
                'status': 'success',
                'questions': result[0]['questions'],
                'subject': result[0]['subject'],
                'ia': result[0]['ia'],
                'semester': result[0]['semester'],
                'time_limit': result[0]['time_limit'],
                'positive_marks': result[0]['positive_marks'],
                'negative_marks': result[0]['negative_marks'],
                'editable': {
                    'status': True,
                } if len(errors) == 0 else {
                    'status': False,
                    'error': errors
                }
            }
            
        else:
            return {
                'status': 'failed',
                'error': 'ITEM_PASSWORD_ERR'
            }


class EditQuiz(Resource):
    def post(self):
        obj = request.get_json(force=True)

        item_password = obj['item_password']
        questions = obj['questions']
        time_limit = obj['time_limit']
        positive_marks = obj['positive_marks']
        negative_marks = obj['negative_marks']

        result = dict(
            mongo.db.items.update(
                {
                    'item_password': item_password
                },

                {
                    '$set': {
                        'questions': questions,
                        'time_limit': time_limit,
                        'positive_marks': positive_marks,
                        'negative_marks': negative_marks
                    }
                }
            )
        )


        if result['nModified'] == 1:
            return {
                'status': 'success'
            }
        else:
            return {
                'status': 'failed'
            }
            

# resources routing
api.add_resource(ShowItemDetails, '/show_item_details')
api.add_resource(EditQuiz, '/edit_quiz')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5056)
