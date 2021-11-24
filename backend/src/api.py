import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

# Redirect after login
@app.route('/login-results')
def show_login_results(): 
    print('hah')
    return 'fuck'

# GET drinks
@app.route('/drinks')
def get_drinks(): 

    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({
        'success': True,
        'drinks': drinks
    })


# GET drink details
@app.route('/drinks-detail')
def get_drinks_detail(): 

    drinks = [drink.long() for drink in Drink.query.all()]
    
    return jsonify({
        'success': True,
        'drinks': drinks
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
# POST drinks
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload): 
    try: 
        body = request.get_json()

        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink(title=title, recipe=json.dumps(recipe))

        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    
    except Exception as e: 
        print(e)
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(payload, id): 
    try: 
        body = request.get_json()
        title = body.get('title', None)
        recipe = body.get('recipe', None)

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None: 
            abort(404)

        drink.title = title
        drink.recipe = json.dumps(recipe)
        
        drink.update()

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    
    except: 
        if drink is None:
            abort(404)
        else:
            abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id): 
    try: 
        drink = Drink.query.filter(Drink.id == id).one_or_none()

        drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })

    except: 
        if drink is None: 
            abort(404)
        else: 
            abort(422)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resorce not found"
    }), 404


@app.errorhandler(AuthError)
def auth_found(error):
    return jsonify({
        "success": False,
        "error": AuthError,
        "message": "authentication error"
    }), AuthError
