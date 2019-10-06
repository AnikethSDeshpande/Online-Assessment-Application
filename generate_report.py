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

# Generate Report API
# Generating report subject wise and presenting it in csv format

class GenerateReport(Resource):
    def post(self):
        obj = request.get_json(force=True)

        return {
            'obj': obj['item_password']
        }
        



# resources routing
api.add_resource(GenerateReport, '/generate_report')


if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5057)
