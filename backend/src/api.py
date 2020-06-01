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


# CORS Headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,POST,PATCH,DELETE,OPTIONS')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_arr = [drink.short() for drink in drinks]
    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks_arr
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    drinks = Drink.query.order_by(Drink.id).all()
    drinks_arr = [drink.long() for drink in drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks_arr
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink():
    try:
        body = request.get_json()
        print(body)
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

        # title and recipe are required
        if new_title is None or new_recipe is None:
            abort(400)

        # preserve title unique constraint
        drink = Drink.query.filter(Drink.title == new_title).one_or_none()
        if drink is not None:
            abort(422)

        drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.short()]
        })

    except Exception:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        body = request.get_json()
        updated_title = body.get('title', None)
        updated_recipe = body.get('recipe', None)

        # title is updated, preserve title unique constraint
        if updated_title is not None and drink.title != updated_title:
            other_drink = Drink.query.filter(
                Drink.title == updated_title).one_or_none()
            if other_drink is not None:
                abort(422)

        drink.title = updated_title if updated_title is not None else drink.title
        drink.recipe = json.dumps(
            updated_recipe) if updated_recipe is not None else drink.recipe
        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.short()]
        })

    except Exception:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'deleted': drink_id
        })

    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
    }), 400


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above, already imported
'''
