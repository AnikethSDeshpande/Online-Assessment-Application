# Author: Aniketh S Deshpande
# API-name: Student-API
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

#StudentSignUp
class StudentSignUp(Resource):
    # checkAvailability is a function that checks if the email_id
    # can be used to create a new account
    def checkAvailability(self, obj):
        mongo_obj = list(mongo.db.student_details.find({'email_id': obj['email_id']}))
        if len(mongo_obj)>0:
            return False
        else:
            return True

    # POST: adding new user to the database if checkAvailability returns TRUE
    def post(self):
        obj = request.get_json(force=True)

        if self.checkAvailability(obj) == True:
           mongo.db.student_details.insert({
               'username': obj['username'],
               'email_id': obj['email_id'],
               'password': obj['password']
           })
           return {
               'status': 'success',
               'email_id': obj['email_id']
               }
        
        else:
            return {
                'status': 'failed',
                'error': 'email_id: {} already used'.format(obj['email_id'])
                }


# AddStudentDetails

class AddStudentDetails(Resource):
    def post(self):
        obj = request.get_json(force=True)

        email_id = obj['email_id']
        student_details = obj['details']

        result = mongo.db.student_details.update(
            {
                'email_id': email_id
            },
            {
                '$set': {
                    'details': student_details
                }
            }
        )

        if result:
            return {
                "status": "success",
                "email_id": email_id
            }
        else:
            return {
                "status": "failed",
                "error": "email_id_error"
            }


    
# LOGIN-API
class StudentLogin(Resource):

    # authenticate is a function that authenticates the username and password
    def authenticate(self, obj):
        mongo_obj = list(mongo.db.student_details.find({
            'email_id': obj['email_id'],
            'password': obj['password']
            }))
        if len(mongo_obj)==1:
            return True, obj['email_id'], mongo_obj[0]['username'], mongo_obj[0]['details']
        else:
            return False, ''

    # genToken: generates a token that will be used throughout the login seesion
    def genToken(self, username):
        KEY = str(randint(100, 1000)) + username + str(randint(100, 1000))
        token = sha1(KEY.encode())
        return token.hexdigest()

    # POST: checking if the user credentials are authentic
    def post(self):
        obj = request.get_json(force=True)
        auth, email_id, username, details = self.authenticate(obj)


        if  auth == True:
           return {
               'status': 'success',
               'token' : self.genToken(username),
               'details': details,
               'username': username,
               'email_id': email_id 
           }
        
        else:
            return {
                'error': 'check login credentials',
                'status': 'failed'
                }



# resources routing
api.add_resource(StudentSignUp, '/student_sign_up')
api.add_resource(AddStudentDetails, '/add_student_details')
api.add_resource(StudentLogin, '/student_login')

if __name__ == '__main__':
    app.run(debug=True, host=ip_address, port=5052)

