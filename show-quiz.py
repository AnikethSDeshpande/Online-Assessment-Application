# Author: Aniketh S Deshpande
# API-name: ShowQuiz-API
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


# StudentPassKeyAuth
class SudentPassKeyAuth(Resource):
    def format_questions(self, item_password):
        question_paper = list(mongo.db.items.find({
                'item_password': item_password
            }))
        
        time_limit = question_paper[0]['time_limit']

        questions = []
        if len(question_paper) == 1:
            questions = [
                    { 
                        'qno': question['qno'], 
                        'question': question['question'], 
                        'options': question['options']
                    } for question in question_paper[0]['questions']
                ]
            
            return {
                'status': 'success',
                'questions': questions,
                'time_limit': time_limit
            }
        
        else:
            return {
                'status': 'failed',
                'error' : 'item_password_error'
            } 


    def post(self):
        obj = request.get_json(force=True)
        email_id = obj['email_id']
        item_password = obj['item_password']

        responses = list(mongo.db.responses.find({
            "email_id": email_id,
            "item_password": item_password
        }))

        if len(responses)>0:
            return {
                'status': 'failed',
                'error' : 'test_repeat_error' 
            }
        else:
            return self.format_questions(item_password)


# StudentResponseHandler
class StudentResponseHandler(Resource):

    def get_score(self, item_password, student_response):
        question_paper = list(mongo.db.items.find({"item_password": item_password}))

        actual_answers = [
                    { 
                        'qno': question['qno'], 
                        'answer': question['answer']
                    } for question in question_paper[0]['questions']
                ]
        
        student_answers = [
                {
                    'qno': stu['qno'],
                    'student_answer': stu['student_answer'] 
                } for stu in student_response
            ]

        score = 0
        for i, (aa,sa) in enumerate(zip(actual_answers, student_answers)):
            if aa['answer'] == sa['student_answer']:
                student_response[i]['status'] = "correct"
                score += 1
            else:
                student_response[i]['status'] = "wrong"

        return score, student_response

    def post(self):
        obj = request.get_json(force=True)
        email_id = obj['email_id']
        item_password = obj['item_password']
        student_response = obj['student_response']

        score, processed_student_response = self.get_score(item_password, student_response)
        
        result = mongo.db.responses.insert({
            "email_id": email_id,
            "item_password": item_password,
            "student_response": processed_student_response,
            "score": score
        })

        if result:
            return {
                "status": "success",
                "email_id": email_id,
                "pass_key": item_password,
                "student_response": processed_student_response,
                "score": score
            }
        
        else:
            return {
                "status": "failed",
                "error": "database_error"
            }



# resources routing
api.add_resource(SudentPassKeyAuth, '/student_pass_key_auth')
api.add_resource(StudentResponseHandler, '/student_response')


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5053)

