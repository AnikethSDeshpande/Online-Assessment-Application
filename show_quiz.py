# Author: Aniketh S Deshpande
# API-name: ShowQuiz-API
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from random import randint, shuffle
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
    def format_questions(self, item_password, email_id):
        question_paper = list(mongo.db.items.find({
                'item_password': item_password
            }))
        

        def shuffle_options(options):
            shuffle(options)
            return options

        questions = []
        if len(question_paper) == 1:
            if (question_paper[0]['gate'] == '__open__' or email_id == '_escape_'):
                time_limit = question_paper[0]['time_limit']
                
                questions = [
                        { 
                            'qno': question['qno'], 
                            'question': question['question'], 
                            'options': shuffle_options(question['options'])
                        } for question in question_paper[0]['questions']
                    ]
                positive_marks = question_paper[0]['positive_marks']
                negative_marks = question_paper[0]['negative_marks']
                
                # shuffling the questions if the request is not from faculty
                if not email_id == '_escape_':
                    shuffle(questions)
                
                # NA_NA and 0_0 is the condition when the student is displayed
                # the question paper but he hasn't submitted his answers successfully.
                # When there is successful submission, the keys- student_response and
                # score get updated to proper values.

                if not email_id == '_escape_':
                    result = mongo.db.responses.insert({
                        "email_id": email_id,
                        "item_password": item_password,
                        "student_response": "NA_NA",
                        "score": "0_0"
                    }
                    )

                return {
                    'status': 'success',
                    'questions': questions,
                    'time_limit': time_limit,
                    'positive_marks': positive_marks,
                    'negative_marks': negative_marks
                }
            
            else:
                return {
                    'status': 'failed',
                    'error' : 'gate_close_error'
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
            return self.format_questions(item_password, email_id)


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

        positive_marks = question_paper[0]['positive_marks']
        negative_marks = question_paper[0]['negative_marks']

        score = 0
        for i, (aa,sa) in enumerate(zip(actual_answers, student_answers)):
            if aa['answer'] == sa['student_answer']:
                student_response[i]['status'] = "correct"
                score += positive_marks
            elif sa['student_answer'] == 'NA':
                student_response[i]['status'] = "NA"
            else:
                student_response[i]['status'] = "wrong"
                score += negative_marks

            student_response[i]['actual_answer'] = aa['answer']
        
        return score, student_response

    def post(self):
        obj = request.get_json(force=True)
        email_id = obj['email_id']
        item_password = obj['item_password']
        student_response = obj['student_response']

        score, processed_student_response = self.get_score(item_password, student_response)
        
        # updating the keys- student_response and score

        result = mongo.db.responses.update({
                "email_id": email_id,
                "item_password": item_password
            },
            {
                "$set": {
                    "student_response": processed_student_response,
                    "score": score
                }
            }
            )

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

