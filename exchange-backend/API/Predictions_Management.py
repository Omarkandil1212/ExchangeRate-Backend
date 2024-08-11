from flask import request, jsonify, Blueprint

import datetime
import pandas as pd
import numpy as np
import requests

from ..app import model, scaler, scaler_y
from .URLS import exchange_rate_management

predictions_management = Blueprint('predictions_management', __name__)

#This function predicts the rate based on the built model
#It takes as input the date for prediction, and the rates of last 3 days.
def predict_exchange_rate(date, prev_rate_1, prev_rate_2, prev_rate_3):
    date_ordinal = pd.to_datetime(date).toordinal()
    date_scaled = scaler.transform([[prev_rate_1, prev_rate_2, prev_rate_3, date_ordinal]])
    date_reshaped = np.reshape(date_scaled, (1, 1, 4))
    predicted_rate = model.predict(date_reshaped, verbose = 0)
    return scaler_y.inverse_transform(predicted_rate[0])[0][0]

#This function is used to manage the response of getting the previous rates for last 3 days
#if the last 3 days are null, the rate of last 3 days is taken to be 89600.
def manage_response(prev_rates_response_body):
    rates = [89600, 89600, 89600]
    for i in range(len(prev_rates_response_body)):
        rate = prev_rates_response_body[i]
        if(rate["lbp_to_usd"] == None and rate["usd_to_lbp"] == None):
            pass
        elif(rate["lbp_to_usd"] == None and rate["usd_to_lbp"] != None):
            rates[i] = rate["usd_to_lbp"]
        elif(rate["lbp_to_usd"] != None and rate["usd_to_lbp"] == None):
            rates[i] = rate["lbp_to_usd"]
        else:
            rates[i] = (rate["lbp_to_usd"]+rate["usd_to_lbp"])/2
    return rates
        
#This route is intended to predict the rate for a specified date that the user provides. 
@predictions_management.route('/', methods = ['GET'], strict_slashes=False)
def predictRate():
    try:
        YEAR, MONTH, DAY = request.args["YEAR"], request.args["MONTH"], request.args["DAY"]
        if(YEAR!="" and MONTH!="" and DAY!=""):
            DATE = datetime.datetime(year=int(YEAR), month=int(MONTH), day=int(DAY), hour=23, minute=59, second=59)
        else:
            return jsonify({"error":"Invalid parameters provided. No parameter should be none"}), 400
    except:
        return jsonify({"error":"Date not provided error in processing start date"}), 400
    if (DATE<=datetime.datetime.today()):
        return jsonify({"error":"Cannot predict for previous days. Predict into the future only"}), 400
    START_DATE = DATE-datetime.timedelta(hours = 72)
    END_DATE = DATE-datetime.timedelta(hours = 24)
    
    if(START_DATE>=datetime.datetime.today() or (START_DATE<datetime.datetime.today() and END_DATE>=datetime.datetime.today())):
        START_DATE = datetime.datetime.today()-datetime.timedelta(hours = 72)
        END_DATE = datetime.datetime.today()-datetime.timedelta(hours = 24)   
 
    
    body = {
        "START_YEAR":START_DATE.year,
        "START_MONTH":START_DATE.month,
        "START_DAY":START_DATE.day,

        "END_YEAR":END_DATE.year,
        "END_MONTH":END_DATE.month,
        "END_DAY":END_DATE.day
    }
    url = exchange_rate_management+"/withDates"
    prev_rates_response = requests.get(url=url, params=body)
    if(prev_rates_response.status_code != 200):
        return prev_rates_response.status_code, prev_rates_response.json() 
    prev_rates = manage_response(prev_rates_response.json())
    rate = float(predict_exchange_rate(DATE, prev_rates[2], prev_rates[1], prev_rates[0]))
    return jsonify({"rate_prediction":rate}),200


