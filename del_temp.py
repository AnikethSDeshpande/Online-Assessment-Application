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

class Delete(Resource):
    def get(self):
        #obj = request.get_json(force=True)
        item_password = request.args.get('a')
        mongo.db.responses.remove({
            'item_password': item_password
        })

        return {
            'status': 'GM!'
        }

            

# resources routing
api.add_resource(Delete, '/del_temp')
# api.add_resource(EditQuiz, '/edit_quiz')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=9999)
