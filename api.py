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


# SIGNUP-API
class SignUp(Resource):

    # checkAvailability is a function that checks if the email_id
    # can be used to create a new account
    def checkAvailability(self, obj):
        mongo_obj = list(mongo.db.login.find({'email_id': obj['email_id']}))
        if len(mongo_obj)>0:
            return False
        else:
            return True

    # POST: adding new user to the database if checkAvailability returns TRUE
    def post(self):
        obj = request.get_json(force=True)

        if self.checkAvailability(obj) == True:
           mongo.db.login.insert({
               'username': obj['username'],
               'email_id': obj['email_id'],
               'password': obj['password']
           })
           return {
               'status': 'success'
               }
        
        else:
            return {
                'status': 'failed',
                'error': 'email_id: {} already used'.format(obj['email_id'])
                }

    
# LOGIN-API
class Login(Resource):

    # authenticate is a function that authenticates the username and password
    def authenticate(self, obj):
        mongo_obj = list(mongo.db.login.find({
            'email_id': obj['email_id'],
            'password': obj['password']
            }))
        if len(mongo_obj)==1:
            return True, mongo_obj[0]['username']
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
        auth, username = self.authenticate(obj)
        if  auth == True:
           return {
               'status': 'success',
               'token' : self.genToken(username),
               'username': username
           }
        
        else:
            return {
                'error': 'check login credentials',
                'status': 'failed'
                }


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
    def getQuestions(self):
        obj = request.get_json()
        print(obj['questions'])
        return obj['questions']    




# Tables-API

class T_entries(Resource):
    def get(self):
        t_array = []
        for item in mongo.db.t.find():
            t_array.append([item['number'],  int(item['size']), int(item['occupancy']) ])
        return {'table': t_array}
    
    def post(self):
        obj = request.get_json(force=True)
        mongo.db.t.insert(obj)
        return {'object_posted': str(obj)}

    def update(self):
        obj = request.get_json(force=True)
        number, new_size, new_occupancy = obj['number'], obj['new_size'], obj['new_occupancy']
        mongo.db.t.update({'number': number}, {'$set':{'occupancy': new_occupancy}})
        return {'object_updated': str(obj)}
        
    def delete(self):
        obj = request.get_json(force=True)
        name = obj['name']
        mongo.db.q.delete({'name': name})
        return {'object_deleted': str(obj)}


# resources routing
api.add_resource(SignUp, '/sign_up')
api.add_resource(Login, '/login')
api.add_resource(NewItem, '/new_item')

if __name__ == '__main__':
    app.run(debug=True, host='10.10.5.25')
