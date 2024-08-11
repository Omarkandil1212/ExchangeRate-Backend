from flask import abort, request, jsonify, Blueprint
import requests
import time

from ..model.transaction import transaction_schema, transactions_schema, Transaction
from ..app import db
from .URLS import user_management_url, exchange_rate_management, notifications_management

transaction_management = Blueprint('transaction_management', __name__)

counter = 0
old_usd_to_lbp = 1
old_lbp_to_usd = 1
old_usd_to_lbp_continuous = 1
old_lbp_to_usd_continuous = 1

#This route is inteneded to add a transaction to the database. It then sends notifications to users acccordingly.
@transaction_management.route('/', methods = ['POST'], strict_slashes=False)
def add_transaction():
    global counter
    global old_usd_to_lbp
    global old_lbp_to_usd
    global old_usd_to_lbp_continuous
    global old_lbp_to_usd_continuous
    try:
        usd_amount = request.json['usd_amount']
        lbp_amount = request.json['lbp_amount']
        usd_to_lbp = request.json['usd_to_lbp']
    except:
        return jsonify({"error":"Missing values or values with incorrect names in the json"}), 400
    if(usd_amount == None or lbp_amount == None or usd_to_lbp == None):
        return jsonify({"error":"Values given should not be empty"}), 400
    if((type(usd_amount) != int and type(usd_amount) != float) or (type(lbp_amount) != int and type(lbp_amount) != float)):
        return jsonify({"error":"USD and LBP amounts should be numbers"}), 400
    if(usd_amount <= 0 or lbp_amount <= 0):
        return jsonify({"error":"Values given should be greater than 0"}), 400
    if(usd_to_lbp != 1 and usd_to_lbp != 0):
        return jsonify({"error":"Please specify type of transaction"}), 400
    
    headers = dict(request.headers)
    user_response = requests.get(user_management_url, headers=headers)
    if(user_response.status_code == 500):
        user_id = None
    else:
        try:
            user = user_response.json()
            user_id = user["id"]
        except:
            user_id = None
    oldRates = requests.get(exchange_rate_management).json()
    if(counter%20 == 0):
        old_usd_to_lbp = oldRates["usd_to_lbp"]
        old_lbp_to_usd = oldRates["lbp_to_usd"]
    old_usd_to_lbp_continuous = oldRates["usd_to_lbp"]
    old_lbp_to_usd_continuous = oldRates["lbp_to_usd"]
    t = Transaction(usd_amount,lbp_amount,usd_to_lbp, user_id)
    db.session.add(t)
    db.session.commit()
    time.sleep(0.5)
    newRates = requests.get(exchange_rate_management).json()
    new_usd_to_lbp = newRates["usd_to_lbp"]
    new_lbp_to_usd = newRates["lbp_to_usd"]
    if(old_lbp_to_usd == None):
        old_lbp_to_usd = 1
    if(old_usd_to_lbp == None):
        old_usd_to_lbp = 1
    if(new_lbp_to_usd == None):
        new_lbp_to_usd = old_lbp_to_usd
    if(new_usd_to_lbp == None):
        new_usd_to_lbp = old_usd_to_lbp
    notif_management = requests.get(notifications_management+f"/manageNotifications?old_usd_to_lbp={old_usd_to_lbp}&new_usd_to_lbp={new_usd_to_lbp}&old_lbp_to_usd={old_lbp_to_usd}&new_lbp_to_usd={new_lbp_to_usd}")
    private_notif_management = requests.get(notifications_management+f"/manageUserSpecificNotifications?old_usd_to_lbp={old_usd_to_lbp_continuous}&new_usd_to_lbp={new_usd_to_lbp}&old_lbp_to_usd={old_lbp_to_usd_continuous}&new_lbp_to_usd={new_lbp_to_usd}")
    print(notif_management.json())
    if(notif_management.json()["reply1"]=="update_lbp_to_usd"):
        old_lbp_to_usd = new_lbp_to_usd
    if(notif_management.json()["reply2"]=="update_usd_to_lbp"):
        old_usd_to_lbp = new_usd_to_lbp
    old_usd_to_lbp_continuous = new_usd_to_lbp
    old_lbp_to_usd_continuous = new_lbp_to_usd
    counter+=1
    return jsonify(transaction_schema.dump(t)), 200

#This route is inteneded to get all transactions of a certain user when logged in.
@transaction_management.route('/', methods = ['GET'], strict_slashes=False)
def get_user_transactions():
    headers = dict(request.headers)
    user_response = requests.get(user_management_url, headers=headers)
    if(user_response.status_code == 500):
        return jsonify({"error":"Invalid Token!"}), 498
    else:
        try:
            user = user_response.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"Token not provided!"}), 499
        try:
            transactions = Transaction.query.filter_by(user_id = user_id).all()
        except:
            abort(500)
        return transactions_schema.dump(transactions)
