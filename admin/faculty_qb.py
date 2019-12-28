# Author: Aniketh S Deshpande
# API-name: Login
# Flask-Server
# Database: MongoDB

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from flask_cors import CORS
from config import get_ip
from itertools import combinations
import random

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
        
        return {
            'status': 'failed',
            'error': 'QB_NOT_MODIFIED'
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


class GenerateQuestionPaper(Resource):
    def post(self):
        obj = request.get_json(force = True)

        qb_name = obj['qb_name']
        qb_levels = obj['levels']
        no_of_questions = obj['no_of_questions']

        qb = list(
            mongo.db.qbanks.find(
                {
                    "name": qb_name
                }
            )
        )

        questions = qb[0]['questions']

        level_match_questions = []

        for question in questions:
            if question['level'] in qb_levels:
                level_match_questions.append(question)
        
        if len(level_match_questions) >= no_of_questions:
            generated_questions = random.choices(level_match_questions, k=no_of_questions)

            return {
                'status': 'success',
                'generated_questions': generated_questions,
                'note': ['sufficient_questions', no_of_questions, len(generated_questions)]
            }
            # array of note: 
            # note[0] --> sufficient/insufficient
            # note[1] --> number of asked questions
            # note[2] --> number of provided questions
        else:
            generated_questions = level_match_questions

            return {
                'status': 'success',
                'generated_questions': generated_questions,
                'note': ['insufficient_questions', no_of_questions, len(generated_questions)]
            }



# resources routing
api.add_resource(FacultyContributeQB, '/insert_update_qb')  
api.add_resource(GetQBQuestions, '/get_qb_questions')  
api.add_resource(GenerateQuestionPaper, '/generate_question_paper')  

# ipaddress loaded dynamically
if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5059)
