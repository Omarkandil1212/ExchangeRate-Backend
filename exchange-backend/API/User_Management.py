from flask import request, jsonify, Blueprint, abort

import requests
import phonenumbers

from ..model.user import user_schema, User
from ..model.wallet import Wallet
from ..model.user_preferences import UserPreferences, user_preferences_schema, many_user_preferences_schema
from ..app import db
from .utils import check_special_characters, check_special_characters_for_username, check_password_length, check_for_patterns, extract_auth_token, decode_token

from sqlalchemy import or_

from .URLS import user_management_url

from .utils import validate_email

user_management = Blueprint('user_management', __name__)

#This routes adds a user to the database
@user_management.route('/', methods = ['POST'], strict_slashes=False)
def add_user():
    try:
        user_name = request.json['user_name']
        password = request.json['password']
    except:
        return jsonify({"error":"Missing values or values with incorrect names in the json"}), 400
    if(user_name == None or password == None):
        return jsonify({"error":"Values given should not be empty"}), 400
    if(not(check_special_characters(password))):
        return jsonify({"error":"Password is not complex enough"}), 400
    if(not(check_password_length(password))):
        return jsonify({"error":"Password is not long enough"}), 400
    if(not(check_for_patterns(password))):
        return jsonify({"error":"Password has a lot of common patterns and repeated characters"}), 400
    if(len(user_name)>30):
        return jsonify({"error":"username is too long"}), 400
    if(len(user_name)<3):
        return jsonify({"error":"username is too short"}), 400
    if(check_special_characters_for_username(user_name)):
        return jsonify({"error":"Try choosing a differenat username without special characters"}), 400
    user = User(user_name, password)
    try:
        db.session.add(user)
        db.session.commit() 
        wallet = Wallet(user_id=user.id, usd_amount = 50, lbp_amount = 10000000)
        db.session.add(wallet)
        db.session.commit()
        user_prefs = UserPreferences(user_id=user.id)
        db.session.add(user_prefs)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({"error":"Choose different username. Username chosen already in use"}), 400
    return jsonify(user_schema.dump(user)), 200

#This routes fetches a user from the database and returns the object without the password
@user_management.route('/', methods = ['GET'], strict_slashes=False)
def get_user_from_token():
    token = extract_auth_token(request)
    if token is None:
        return jsonify({"error":"Token not provided!"}), 499
    else:
        try:
            user_id = decode_token(token)
        except:
            return jsonify({"error":"Invalid Token!"}), 498
        try:
            user = User.query.filter_by(id=user_id).first()
        except: 
            abort(500)
        if(user is None):
            return jsonify({"error":"Invalid Token!"}), 498
        return jsonify(user_schema.dump(user)), 200

#This routes gets the information of a user from his id. IT IS INTENEDED FOR INTERNAL USE ONLY AND NOT FOR FRONTEND USERS
@user_management.route('/fromId', methods = ['GET'], strict_slashes=False)
def get_user_from_id():
    if request.remote_addr not in ['127.0.0.1']:
        abort(403)
    try:
        user_id = request.args['user_id']
    except:
        return jsonify({"error":"User id not given"}), 400
    if(user_id == None):
        return jsonify({"error":"User id not given"}), 400
    try:
        user = User.query.filter_by(id=user_id).first()
    except:
        abort(500)
    if(user is None):
        return jsonify({"error":"Invalid user id!"}), 498
    return jsonify(user_schema.dump(user)), 200    

#This routes updates the preferences of a user in the database GPT Helped with this function
@user_management.route("/updateUserPreferences", methods=["POST"])
def update_user_preferences():
    # Extract data from the request body
    request_body = request.json
    headers = dict(request.headers)
    userResponse = requests.get(user_management_url, headers=headers)
    if(userResponse.status_code == 500):
        return jsonify({"error":"Invalid Token!"}), 498 
    else:
        try:
            user = userResponse.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"Token not provided!"}), 499
    add_to_table = False
    try:
        try: 
            user_preferences = UserPreferences.query.filter_by(user_id=user_id).first()
        except:
            abort(500)
        # Update bounds if requested
        if user_preferences is None:
            # Handle case where user preferences do not exist
            user_preferences = UserPreferences(user_id)
            add_to_table = True


        if request_body.get("update_bounds", False):
            user_preferences.upper_bound_usd_to_lbp = request_body.get("upper_bound_usd_to_lbp")
            user_preferences.lower_bound_usd_to_lbp = request_body.get("lower_bound_usd_to_lbp")
            user_preferences.upper_bound_lbp_to_usd = request_body.get("upper_bound_lbp_to_usd")
            user_preferences.lower_bound_lbp_to_usd = request_body.get("lower_bound_lbp_to_usd")

        # Update email preference if requested
        if request_body.get("update_email_preference", False):
            email = request_body.get("email")
            send_email = request_body.get("send_email")
            if(send_email and email==None):
                return jsonify({"error":"Email not provided"}), 400
            user_preferences.send_email = send_email
            if(send_email):
                if(not validate_email(email)):
                    return jsonify({"error":"Invalid email"}), 400
                user_preferences.email = email

        # Update SMS preference if requested
        if request_body.get("update_sms_preference", False):
            phone_number = request_body.get("phone_number")
            print(phone_number)
            send_sms = request_body.get("send_sms", False)
            if(send_sms and phone_number==None):
                return jsonify({"error":"Phone number not provided"}), 400
            user_preferences.send_sms = send_sms
            if(send_sms):
                if(not phonenumbers.is_possible_number(phonenumbers.parse(phone_number))):
                    return jsonify({"error":"Invalid phone number"}), 400
                user_preferences.phone_number = phone_number

        # Commit changes to the database
        if(add_to_table):
            db.session.add(user_preferences)
        db.session.commit()
        print("User preferences updated successfully.")


    except Exception as e:
        return jsonify({"error":f"Internal Error happened! {e}"}), 500
    
    return jsonify(user_preferences_schema.dump(user_preferences))

#This routes gets the user preference according to the id of the user. IT IS INTENEDED FOR INTERNAL USE ONLY AND NOT FOR FRONTEND USERS
@user_management.route("/getUserPreferences", methods=["GET"])
def get_user_preferences_from_id():
    if request.remote_addr not in ['127.0.0.1']:
        abort(403)
    # Extract data from the request body
    try:
        user_id = request.json['user_id']
    except:
        return jsonify({"error":"Missing values or values with incorrect names in the json"}), 400
    try: 
        user_preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    except:
        abort(500)
    return jsonify(user_preferences_schema.dump(user_preferences)), 200

#This routes gets the user preference according to the token of the user.
@user_management.route("/getUserPreferencesFromId", methods=["GET"])
def get_user_preferences():
    # Extract data from the request body
    headers = dict(request.headers)
    userResponse = requests.get(user_management_url, headers=headers)
    if(userResponse.status_code == 500):
        return jsonify({"error":"Invalid Token!"}), 498 
    else:
        try:
            user = userResponse.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"Token not provided!"}), 499
    try:
        user_preferences = UserPreferences.query.filter_by(user_id=user_id).first()
    except:
        abort(500)  
    return jsonify(user_preferences_schema.dump(user_preferences)), 200

#This routes gets the all preferences of all users from the database. IT IS INTENEDED FOR INTERNAL USE ONLY AND NOT FOR FRONTEND USERS
@user_management.route("/getAllUserPreferences", methods=["GET"])
def get_all_user_preferences():
    if request.remote_addr not in ['127.0.0.1']:
        abort(403)
    # Extract data from the request body
    try:
        user_preferences = UserPreferences.query.all()
    except: 
        abort(500)
    return jsonify(many_user_preferences_schema.dump(user_preferences)), 200

#This routes gets the all preferences of all users from the database. IT IS INTENEDED FOR INTERNAL USE ONLY AND NOT FOR FRONTEND USERS
@user_management.route("/getAllUserPreferencesNotNull", methods=["GET"])
def get_all_user_preferences_not_none():
    # Extract data from the request body
    if request.remote_addr not in ['127.0.0.1']:
        abort(403)
    try:
        user_preferences = UserPreferences.query.filter(   
            or_(
                UserPreferences.upper_bound_usd_to_lbp.isnot(None),
                UserPreferences.lower_bound_usd_to_lbp.isnot(None),
                UserPreferences.upper_bound_lbp_to_usd.isnot(None),
                UserPreferences.lower_bound_lbp_to_usd.isnot(None)
            )
        ).all()
    except:
        abort(500)
    return jsonify(many_user_preferences_schema.dump(user_preferences)), 200

