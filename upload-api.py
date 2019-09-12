# Author: Aniketh S Deshpande
# API-name: Uplaod-Items
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


# New-Item-API
class NewItem(Resource):

    def post(self):
        obj = request.get_json(force=True)
        
        username = obj['username']    # name of the user creating the quiz
        item_type = obj['item_type']  # IA test/ACM/Technosparks/others
        subject = obj['subject']      # CO/OOPS/MPMC
        ia = obj['ia']                # 1/2/3 **optional
        semester = obj['semester']    # 3/5/7

        item_name = str(username) + '_' + str(item_type) + '_' + str(subject) + '_' + str(ia) + '_' + str(semester)

        return {
            'item_name': item_name,
            'subject': subject,
            'ia': ia,
            'semester': semester
            }


class UploadQuestions(Resource):

    def checkAvailability(self, password):
        mongo_obj = list(mongo.db.items.find({'item_password': password}))
        if len(mongo_obj)>0:
            return False
        else:
            return True


    def post(self):
        obj = request.get_json(force=True)
        password = obj['item_password']

        if self.checkAvailability(password) == True:
            obj['registrations'] = []
            obj['responses'] = []
            result = mongo.db.items.insert(obj)
            
            if result:
                return {
                    "status": "success",
                    "id": str(sha1(str(result).encode()))
                    }
            else:
                return {
                    "status": "failed",
                    "error": "DBError"
                }
        
        else:
            return {
                'status': 'failed',
                'error': 'exam_key not unique' 
            }

# resources routing
api.add_resource(NewItem, '/new_item_name')
api.add_resource(UploadQuestions, '/upload_questions')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5051)
