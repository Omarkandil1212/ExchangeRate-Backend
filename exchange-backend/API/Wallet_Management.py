from flask import request, jsonify, Blueprint, abort

import requests

from ..model.wallet import wallet_schema, Wallet
from ..app import db

from .URLS import user_management_url

wallet_management = Blueprint('wallet_management', __name__)

#This route fetches the wallet amounts of users based on their tokens from the database and returns it
@wallet_management.route('/', methods = ['GET'], strict_slashes = False)
def get_wallet_values():
    headers = dict(request.headers)
    userResponse = requests.get(user_management_url, headers=headers)
    if(userResponse.status_code == 500):
        return jsonify({"error":"Invalid Token"}), 400
    else:
        try:
            user = userResponse.json()
            user_id = user["id"]
            print(user_id)
        except:
            return jsonify({"error":"Invalid Token"}), 400
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
    except:
        abort(500)
    if wallet == None:
        return jsonify({"error":"No wallet is associated with this account"}), 400
    return jsonify(wallet_schema.dump(wallet)), 200

#This route is used internally and not intended for public use. It allows updating the value of wallets of a user in the database
@wallet_management.route('/updateWallet', methods = ['POST'])
def update_wallet_values():
    try:
        usd_to_add = request.json['usd_to_add']
        lbp_to_add = request.json['lbp_to_add']
        user_id = request.json['user_id']
    except:
        return jsonify({"error":"Missing values or values with incorrect names in the json"}), 400    
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).first()
    except:
        abort(500)
    if wallet == None:
        return jsonify({"error":"No wallet is associated with this account"}), 400
    wallet.usd_amount += usd_to_add
    wallet.lbp_amount += lbp_to_add
    db.session.commit()
    return jsonify(wallet_schema.dump(wallet)), 200