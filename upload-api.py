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

app = Flask(__name__)
CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/quiz"
api = Api(app)
mongo = PyMongo(app)


# New-Item-API
class NewItem(Resource):
    def create_new_item(self, obj):
        pass

    def post(self):
        obj = request.get_json(force=True)
        
        username = obj['username']    # name of the user creating the quiz
        item_type = obj['item_type']  # IA test/ACM/Technosparks/others
        subject = obj['subject']      # CO/OOPS/MPMC
        ia = obj['ia']                # 1/2/3 **optional
        semester = obj['semester']    # 3/5/7

        item_name = str(username) + '_' + str(item_type) + '_' + str(subject) + '_' + str(ia) + '_' + str(semester)

        return {'item_name': item_name}


class UploadQuestions(Resource):
    def post(self):
        obj = request.get_json(force=True)

        result = mongo.db.items.insert(obj)
        print(result)
        return str(result)




# resources routing
api.add_resource(NewItem, '/new_item')
api.add_resource(UploadQuestions, '/upload_questions')

if __name__ == '__main__':
    app.run(debug=True, host='10.10.5.240', port=5051)

