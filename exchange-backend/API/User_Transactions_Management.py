import datetime
from flask import request, jsonify, Blueprint, abort
import requests

from ..model.user_transactions import user_transactions_schema, many_user_transactions_schema, UserTransactions
from ..app import db
from .URLS import user_management_url, transaction_management, wallet_management

from .utils import create_token

user_transaction_management = Blueprint('user_transaction_management', __name__)

#This route adds a transaction that could be accepted by other users
@user_transaction_management.route('/', methods = ['POST'], strict_slashes=False)
def add_transaction():
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
        return jsonify({"error":"You need to be logged in to add transaction between users"}), 401
    else:
        try:
            user = user_response.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"You need to be logged in to add transaction between users"}), 401
    wallet_response = requests.get(url=wallet_management, headers=headers)
    if(wallet_response.status_code != 200):
        return jsonify({"error":"Invalid wallet"}), 400
    wallet = wallet_response.json()
    if(usd_to_lbp and wallet["usd_amount"]<usd_amount):
        return jsonify({"error":"Not enough money to post transaction"}), 400
    if(not(usd_to_lbp) and wallet["lbp_amount"]<lbp_amount):
        return jsonify({"error":"Not enough money to proceed transaction"}), 400
    t = UserTransactions(usd_amount,lbp_amount,usd_to_lbp, user_id)
    db.session.add(t)
    db.session.commit()
    transaction = user_transactions_schema.dump(t)
    user1_id = transaction["user1_id"]
    body = {"user_id":user1_id}
    user_response = requests.get(user_management_url+"/fromId", params=body)
    if(user_response.status_code!=200):
        return user_response.json(), 500
    user1 = user_response.json()
    user2_id = transaction["user2_id"]
    if(user2_id!=None):
        
        body = {"user_id":user2_id}
        user_response = requests.get(user_management_url+"/fromId", params=body)
        if(user_response.status_code!=200):
            return user_response.json(), 500
        user2 = user_response.json()
    else:
        user2 = {
                    "id": None,
                    "user_name": None
                }
    transaction["user1"] = user1
    transaction["user2"] = user2
    return jsonify(transaction), 200

#This route gets all transactions that are not accepted posted by all users
@user_transaction_management.route('/', methods = ['GET'], strict_slashes=False)
def get_all_transactions():
    users = {}
    try:
        user_transactions = UserTransactions.query.filter_by(accepted=False).order_by(UserTransactions.added_date)
    except:
        abort(500)
    to_return = many_user_transactions_schema.dump(user_transactions)
    for transaction in to_return:
        user1_id = transaction["user1_id"]
        if user1_id in users:
            user1 = users[user1_id]
        else:
            body = {"user_id":user1_id}
            user_response = requests.get(user_management_url+"/fromId", params=body)
            if(user_response.status_code!=200):
                return user_response.json(), 500
            user1 = user_response.json()
        users[user1_id] = user1
        user2_id = transaction["user2_id"]
        if(user2_id!=None):
            if user2_id in users:
                user2 = users[user2_id]
            else:
                body = {"user_id":user2_id}
                user_response = requests.get(user_management_url+"/fromId", params=body)
                if(user_response.status_code!=200):
                    return user_response.json(), 500
                user2 = user_response.json()
        else:
            user2 = {
                        "id": None,
                        "user_name": None
                    }
        users[user2_id] = user2
        transaction["user1"] = user1
        transaction["user2"] = user2
    return to_return, 200    

#This route gets the accepted transactions of a specific user. It gets transactions posted by the user and accepted or accepted by the user 
@user_transaction_management.route('/userSpecific', methods = ['GET'])
def get_user_transactions():
    users = {}
    headers = dict(request.headers)
    user_response = requests.get(user_management_url, headers=headers)
    if(user_response.status_code == 500):
        return jsonify({"error":"You need to be logged in to add transaction between users"}), 401
    else:
        try:
            user = user_response.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"You need to be logged in to add transaction between users"}), 401
    try:
        user_transactions = UserTransactions.query.filter((((UserTransactions.user1_id == user_id) | (UserTransactions.user2_id == user_id)) & UserTransactions.accepted == True)).order_by(UserTransactions.added_date)
    except:
        abort(500)
    to_return = many_user_transactions_schema.dump(user_transactions)
    for transaction in to_return:
        user1_id = transaction["user1_id"]
        if user1_id in users:
            user1 = users[user1_id]
        else:
            body = {"user_id":user1_id}
            user_response = requests.get(user_management_url+"/fromId", params=body)
            if(user_response.status_code!=200):
                return user_response.json(), 500
            user1 = user_response.json()
        users[user1_id] = user1
        user2_id = transaction["user2_id"]
        if(user2_id!=None):
            if user2_id in users:
                user2 = users[user2_id]
            else:
                body = {"user_id":user2_id}
                user_response = requests.get(user_management_url+"/fromId", params=body)
                if(user_response.status_code!=200):
                    return user_response.json(), 500
                user2 = user_response.json()
        else:
            user2 = {
                        "id": None,
                        "user_name": None
                    }
        users[user2_id] = user2
        transaction["user1"] = user1
        transaction["user2"] = user2
    return to_return, 200

#This route allows users to accept a certain transaction posted by other user if the wallet balance of both users is allows this
@user_transaction_management.route('/acceptTransaction', methods = ['POST'])
def accept_transaction():
    try:
        transaction_id = request.json["transaction_id"]
    except Exception as e:
        return jsonify({"error":"Missing transaction id"}), 400
    if transaction_id == None:
        return jsonify({"error":"Missing transactio=n id"}), 400 
    headers = dict(request.headers)
    user_response = requests.get(user_management_url, headers=headers)
    if(user_response.status_code == 500):
        return jsonify({"error":"You need to be logged in to add transaction between users"}), 401
    else:
        try:
            user = user_response.json()
            user_id = user["id"]
        except:
            return jsonify({"error":"You need to be logged in to add transaction between users"}), 401    
    try:
        transaction = UserTransactions.query.filter_by(id=transaction_id).first()
    except:
        abort(500)
    if(transaction.accepted == True):
        return jsonify({"error":"Cannot accept an accepted transaction"}), 400 
    if(transaction.user1_id == user_id):
        return jsonify({"error":"Cannot accept your own transaction"}), 400  
    
    wallet_response_1 = requests.get(url=wallet_management, headers=headers) #wallet1 the one accepting
    if(wallet_response_1.status_code != 200):
        return jsonify({"error":"Invalid wallet"}), 400
    wallet_1 = wallet_response_1.json()
    token = create_token(user_id=transaction.user1_id)
    headerr = {'Authorization':f"Bearer {token}"}
    wallet_response_2 = requests.get(url=wallet_management, headers=headerr)
    if(wallet_response_2.status_code!=200):
        return jsonify({"error":"Invalid wallet"}), 400
    wallet_2 = wallet_response_2.json() #wallet2 the one who posted the transaction
    print(wallet_1)
    print(wallet_2)
    if((transaction.usd_to_lbp) and (wallet_2["usd_amount"]<transaction.usd_amount or wallet_1["lbp_amount"]<transaction.lbp_amount)):
        return jsonify({"error":"Not enough money to proceed with the transaction"}), 400
    elif((transaction.usd_to_lbp)):
        usd_to_add_in_user_1 = -transaction.usd_amount
        usd_to_add_in_user_2 = transaction.usd_amount
        lbp_to_add_in_user_1 = transaction.lbp_amount
        lbp_to_add_in_user_2 = -transaction.lbp_amount
    if(not(transaction.usd_to_lbp) and (wallet_1["usd_amount"]<transaction.usd_amount or wallet_2["lbp_amount"]<transaction.lbp_amount)):
        return jsonify({"error":"Not enough money to post transaction"}), 400
    elif(not(transaction.usd_to_lbp)):
        usd_to_add_in_user_1 = transaction.usd_amount
        usd_to_add_in_user_2 = -transaction.usd_amount
        lbp_to_add_in_user_1 = -transaction.lbp_amount
        lbp_to_add_in_user_2 = transaction.lbp_amount
    body_of_post = {'user_id':transaction.user1_id, 'usd_to_add':usd_to_add_in_user_1, 'lbp_to_add':lbp_to_add_in_user_1}
    requestt = requests.post(url=wallet_management+'/updateWallet', json=body_of_post)
    if(requestt.status_code!=200):
        return jsonify({"error":"Internal error"}), 500
    
    body_of_post = {'user_id':user_id, 'usd_to_add':usd_to_add_in_user_2, 'lbp_to_add':lbp_to_add_in_user_2}
    requestt = requests.post(url=wallet_management+'/updateWallet', json=body_of_post)
    if(requestt.status_code!=200):
        return jsonify({"error":"Internal error"}), 500
    transaction.accepted = True
    transaction.date_accepted = datetime.datetime.now()
    transaction.user2_id = user_id
    db.session.commit()
    body_of_post = {"usd_amount":transaction.usd_amount,
                "lbp_amount":transaction.lbp_amount,
                "usd_to_lbp":transaction.usd_to_lbp,
            }
    requestt = requests.post(url=transaction_management, json=body_of_post, headers=headerr)
    if(requestt.status_code!=200):
        return jsonify({"error":"Internal error when adding transaction to DB"}), 500
    to_return = user_transactions_schema.dump(transaction)
    user1_id = to_return["user1_id"]
    body = {"user_id":user1_id}
    user_response = requests.get(user_management_url+"/fromId", params=body)
    if(user_response.status_code!=200):
        return user_response.json(), 503
    user1 = user_response.json()
    user2_id = to_return["user2_id"]
    body = {"user_id":user2_id}
    user_response = requests.get(user_management_url+"/fromId", params=body)
    if(user_response.status_code!=200):
        return user_response.json(), 500
    user2 = user_response.json()
    to_return["user1"] = user1
    to_return["user2"] = user2
    return to_return, 200

