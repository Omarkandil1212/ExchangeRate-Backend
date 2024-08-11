from flask import request, jsonify, Blueprint, abort

from threading import Thread

from sqlalchemy import or_

from ..app import socket, db
from ..model.user_sid import UserSid
from .URLS import user_management_url

import requests

from .utils import send_mails_to_users, send_mails_to_multiple_users

notifications_management = Blueprint('notifications_management', __name__)

#This is used when a user logs in and wants to log his sid into the database
@socket.on('send_token_java')
def get_token_java(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    user_sid = request.sid
    if(user_sid_link == None):
        user_sid_link = UserSid(user_id)
        db.session.add(user_sid_link)
    user_sid_link.user_sid_java = user_sid
    db.session.commit()    
    return    

@socket.on('send_token_android')
def get_token_android(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    user_sid = request.sid
    if(user_sid_link == None):
        user_sid_link = UserSid(user_id)
        db.session.add(user_sid_link)
    user_sid_link.user_sid_android = user_sid
    db.session.commit()    
    return    

@socket.on('send_token_react')
def get_token_react(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    user_sid = request.sid
    if(user_sid_link == None):
        user_sid_link = UserSid(user_id)
        db.session.add(user_sid_link)
    user_sid_link.user_sid_react = user_sid
    db.session.commit()    
    return    


#This is used when a user logs out and wants to remove hs sid from the database i order not to receive specific notifications
@socket.on('remove_sid_java')
def remove_sid_java(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    try:
        user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    except:
        abort(500)
    if(user_sid_link == None):
        return
    user_sid_link.user_sid_java = None
    db.session.commit()    
    return    

@socket.on('remove_sid_android')
def remove_sid_android(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    try:
        user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    except:
        abort(500)
    if(user_sid_link == None):
        return
    user_sid_link.user_sid_android = None
    db.session.commit()    
    return    

@socket.on('remove_sid_react')
def remove_sid_react(token):
    headerr = {'Authorization':f"Bearer {token}"}
    user_request = requests.get(url=user_management_url, headers=headerr)
    if(user_request.status_code!=200):
        return 
    user = user_request.json()
    user_id = user["id"]
    try:
        user_sid_link = UserSid.query.filter_by(user_id = user_id).first()
    except:
        abort(500)
    if(user_sid_link == None):
        return
    user_sid_link.user_sid_react = None
    db.session.commit()    
    return    



#This route is intended to send notifications and emails based on user preferences
#GPT HELPED ME IN THE FOLLOWING FUNCTION
@notifications_management.route("/manageUserSpecificNotifications", methods=["GET"])
def send_notifications_specific():
    try:
        old_usd_to_lbp = float(request.args.get('old_usd_to_lbp'))
        new_usd_to_lbp = float(request.args.get('new_usd_to_lbp'))
        old_lbp_to_usd = float(request.args.get('old_lbp_to_usd'))
        new_lbp_to_usd = float(request.args.get('new_lbp_to_usd'))
    except (TypeError, ValueError):
        return jsonify({"error": "Missing or invalid parameters"}), 400

    try:
        percent_change_usd_to_lbp = (new_usd_to_lbp - old_usd_to_lbp) / old_usd_to_lbp * 100
        percent_change_lbp_to_usd = (new_lbp_to_usd - old_lbp_to_usd) / old_lbp_to_usd * 100
    except ZeroDivisionError:
        return jsonify({"error": "One of the old exchange rates is zero"}), 400

    # Fetch user session IDs
    user_sid_query = UserSid.query.filter(
                                            or_(
                                                UserSid.user_sid_java != None,
                                                UserSid.user_sid_android != None,
                                                UserSid.user_sid_react != None
                                            )
                                        ).all()

    user_sid_dict_java = {}
    user_sid_dict_android = {}
    user_sid_dict_react = {}
    for user_sid in user_sid_query:
        if(user_sid.user_sid_java != None):
            user_sid_dict_java[user_sid.user_id]= user_sid.user_sid_java
    for user_sid in user_sid_query:
        if(user_sid.user_sid_android != None):
            user_sid_dict_android[user_sid.user_id]= user_sid.user_sid_android
    for user_sid in user_sid_query:
        if(user_sid.user_sid_react != None):
            user_sid_dict_react[user_sid.user_id]= user_sid.user_sid_react    
    # Fetch user preferences
    user_preferences_response = requests.get(user_management_url + '/getAllUserPreferencesNotNull')
    user_preferences = user_preferences_response.json()

    emails_messages = []
    
    # Check and prepare notifications for rate changes
    for user_preference in user_preferences:
        user_id = user_preference['user_id']
        email = user_preference["email"]
        message = None
        # LBP to USD checks
        if percent_change_lbp_to_usd != 0:
            bound_key = 'upper_bound_lbp_to_usd' if percent_change_lbp_to_usd > 0 else 'lower_bound_lbp_to_usd'
            bound_value = user_preference.get(bound_key)
            if bound_value and ((percent_change_lbp_to_usd > 0 and new_lbp_to_usd >= bound_value and old_lbp_to_usd <= bound_value) or
                                (percent_change_lbp_to_usd < 0 and new_lbp_to_usd <= bound_value and old_lbp_to_usd >= bound_value)):
                message = f"The LBP to USD rate is now {'higher' if percent_change_lbp_to_usd > 0 else 'lower'} than {bound_value}"

        # USD to LBP checks
        if percent_change_usd_to_lbp != 0:
            bound_key = 'upper_bound_usd_to_lbp' if percent_change_usd_to_lbp > 0 else 'lower_bound_usd_to_lbp'
            bound_value = user_preference.get(bound_key)
            if bound_value and ((percent_change_usd_to_lbp > 0 and new_usd_to_lbp >= bound_value and old_usd_to_lbp <= bound_value) or
                                (percent_change_usd_to_lbp < 0 and new_usd_to_lbp <= bound_value and old_usd_to_lbp >= bound_value)):
                message = f"The USD to LBP rate is now {'higher' if percent_change_usd_to_lbp > 0 else 'lower'} than {bound_value}"
        
        # Send notifications if conditions are met
        if message and user_id in user_sid_dict_java:
            socket.emit("notification", {
                "Title": "Exchange Rate Alert",
                "Message": message
            }, to=user_sid_dict_java[user_id])
        if message and user_id in user_sid_dict_android:
            socket.emit("notification", {
                "Title": "Exchange Rate Alert",
                "Message": message
            }, to=user_sid_dict_android[user_id])
        if message and user_id in user_sid_dict_react:
            socket.emit("notification", {
                "Title": "Exchange Rate Alert",
                "Message": message
            }, to=user_sid_dict_react[user_id])

        if message and user_preference["send_email"]:
            emails_messages.append((email, message))
    email_thread = Thread(target=send_mails_to_multiple_users, args = (emails_messages,))
    email_thread.start()
    return jsonify({"status": "Notifications sent"}), 200

#This route is intended to send notifications and emails when exchange rate fuctuates for more than 10%
@notifications_management.route("/manageNotifications", methods=["GET"])
def send_notifications():
    try:
        old_usd_to_lbp = float(request.args.get('old_usd_to_lbp'))
        new_usd_to_lbp = float(request.args.get('new_usd_to_lbp'))
        old_lbp_to_usd = float(request.args.get('old_lbp_to_usd'))
        new_lbp_to_usd = float(request.args.get('new_lbp_to_usd'))
    except TypeError:
        return jsonify({"error": "Missing or invalid parameters"}), 400
    except ValueError:
        return jsonify({"error": "One of the parameters is null or invalid (non-numeric)"}), 400
    try:
        percent_change_usd_to_lbp = (new_usd_to_lbp-old_usd_to_lbp)/old_usd_to_lbp * 100
        percent_change_lbp_to_usd = (new_lbp_to_usd-old_lbp_to_usd)/old_lbp_to_usd * 100
    except:
        return jsonify({"error":"One of the parameters is null or zero"}),400

    reply = {"reply1":None, "reply2":None}
    usd_to_lbp_check = False
    if(percent_change_usd_to_lbp<=-10 or percent_change_usd_to_lbp>=10):
        usd_to_lbp_check  = True
        reply["reply2"] = "update_usd_to_lbp"
    lbp_to_usd_check = False
    if(percent_change_lbp_to_usd<=-10 or percent_change_lbp_to_usd>=10):
        lbp_to_usd_check  = True
        reply["reply1"] = "update_lbp_to_usd"
    if(usd_to_lbp_check and lbp_to_usd_check):
        if(percent_change_usd_to_lbp<0):
            state_usd_to_lbp = "decreased"
        elif(percent_change_usd_to_lbp>0):
            state_usd_to_lbp = "increased"
        if(percent_change_lbp_to_usd<0):
            state_lbp_to_usd = "decreased"
        elif(percent_change_lbp_to_usd>0):
            state_lbp_to_usd = "increased"
        message = f"The selling price of USD has {state_usd_to_lbp} {int(percent_change_usd_to_lbp)}% and the buying price of USD has {state_lbp_to_usd} {int(percent_change_lbp_to_usd)}%."
    elif(usd_to_lbp_check and not(lbp_to_usd_check)):
        if(percent_change_usd_to_lbp<0):
            state_usd_to_lbp = "decreased"
        elif(percent_change_usd_to_lbp>0):
            state_usd_to_lbp = "increased"
        message = f"The selling price of USD has {state_usd_to_lbp} {int(percent_change_usd_to_lbp)}%."
    elif(not(usd_to_lbp_check) and lbp_to_usd_check):
        if(percent_change_lbp_to_usd<0):
            state_lbp_to_usd = "decreased"
        elif(percent_change_lbp_to_usd>0):
            state_lbp_to_usd = "increased"
        message = f"The buying price of USD has {state_lbp_to_usd} {int(percent_change_lbp_to_usd)}%."
    if(not(usd_to_lbp_check or lbp_to_usd_check)):
        return jsonify(reply), 200
    socket.emit("notification", {"Title":"Rapid change in the price of USD", "Message":message})
    user_preferences_response = requests.get(user_management_url+'/getAllUserPreferences')
    if(user_preferences_response.status_code != 200):
        return jsonify({'error':'Internal Error'}), 500
    user_preferences = user_preferences_response.json()
    email_thread = Thread(target=send_mails_to_users, args = (user_preferences, message))
    email_thread.start()
    return jsonify(reply), 200
        
