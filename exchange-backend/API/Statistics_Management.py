from flask import request, jsonify, Blueprint, abort
import requests

import datetime

from ..model.transaction import  Transaction
from .URLS import exchange_rate_management
from .utils import calculate_percentage_change

statistics_management = Blueprint('statistics_management', __name__)

#This route gets the minimum and maximum values in a specified date range
@statistics_management.route('/getExtremums', methods = ['GET'])
def get_extremums():
    url = exchange_rate_management+"/withDates"
    response = requests.get(url=url, params=request.args)
    if(response.status_code!=200):
        return response.json(), response.status_code
    exchange_rates = response.json()
    min_lbp_to_usd = None
    max_lbp_to_usd = None
    min_lbp_to_usd_date = None
    max_lbp_to_usd_date = None

    min_usd_to_lbp = None
    max_usd_to_lbp = None
    min_usd_to_lbp_date = None
    max_usd_to_lbp_date = None

    for entry in exchange_rates:
        if entry["lbp_to_usd"] is not None:
            if min_lbp_to_usd is None or entry["lbp_to_usd"] < min_lbp_to_usd:
                min_lbp_to_usd = entry["lbp_to_usd"]
                min_lbp_to_usd_date = entry["date"]
            if max_lbp_to_usd is None or entry["lbp_to_usd"] > max_lbp_to_usd:
                max_lbp_to_usd = entry["lbp_to_usd"]
                max_lbp_to_usd_date = entry["date"]
        if entry["usd_to_lbp"] is not None:
            if min_usd_to_lbp is None or entry["usd_to_lbp"] < min_usd_to_lbp:
                min_usd_to_lbp = entry["usd_to_lbp"]
                min_usd_to_lbp_date = entry["date"]
            if max_usd_to_lbp is None or entry["usd_to_lbp"] > max_usd_to_lbp:
                max_usd_to_lbp = entry["usd_to_lbp"]
                max_usd_to_lbp_date = entry["date"]

    to_return = {
        "min_lbp_to_usd": min_lbp_to_usd,
        "max_lbp_to_usd": max_lbp_to_usd,
        "min_lbp_to_usd_date": min_lbp_to_usd_date,
        "max_lbp_to_usd_date": max_lbp_to_usd_date,
        "min_usd_to_lbp": min_usd_to_lbp,
        "max_usd_to_lbp": max_usd_to_lbp,
        "min_usd_to_lbp_date": min_usd_to_lbp_date,
        "max_usd_to_lbp_date": max_usd_to_lbp_date,
    }
    
    return jsonify(to_return), 200

#This route gets the average of buy and sell usd rate in a specified date range
@statistics_management.route('/getAverageRates', methods = ['GET'])
def get_average():
    url = exchange_rate_management+"/withDates"
    response = requests.get(url=url, params=request.args)
    if(response.status_code!=200):
        return response.json(), response.status_code
    exchange_rates = response.json()
    lbp_to_usd_values = [entry["lbp_to_usd"] for entry in exchange_rates if entry["lbp_to_usd"] is not None]
    usd_to_lbp_values = [entry["usd_to_lbp"] for entry in exchange_rates if entry["usd_to_lbp"] is not None]
    
    if len(lbp_to_usd_values)>0:
        avg_lbp_to_usd = sum(lbp_to_usd_values)/len(lbp_to_usd_values)
    else:
        avg_lbp_to_usd = None
    
    if len(lbp_to_usd_values)>0:
        avg_usd_to_lbp = sum(usd_to_lbp_values)/len(usd_to_lbp_values)
    else:
        avg_usd_to_lbp = None
    
    to_return = {
        "avg_lbp_to_usd":avg_lbp_to_usd,
        "avg_usd_to_lbp":avg_usd_to_lbp,
    }
    
    return jsonify(to_return), 200

#This route gets the precent change in buy and sell usd rate in a specified date range
@statistics_management.route('/getPercentChange', methods = ['GET'])
def get_percent_change():
    url = exchange_rate_management+"/withDates"
    response = requests.get(url=url, params=request.args)
    if(response.status_code!=200):
        return response.json(), response.status_code
    exchange_rates = response.json()
    lbp_to_usd_values = [entry["lbp_to_usd"] for entry in exchange_rates if entry["lbp_to_usd"] is not None]
    usd_to_lbp_values = [entry["usd_to_lbp"] for entry in exchange_rates if entry["usd_to_lbp"] is not None]
    
    percent_lbp_to_usd = calculate_percentage_change(lbp_to_usd_values)
    percent_usd_to_lbp = calculate_percentage_change(usd_to_lbp_values)
    
    to_return = {
        "percent_lbp_to_usd":percent_lbp_to_usd,
        "percent_usd_to_lbp":percent_usd_to_lbp,
    }
    
    return jsonify(to_return), 200

#This route gets the volumes of transactions in a specified date range
@statistics_management.route('/getVolumes', methods = ['GET'])
def get_volumes():
    try:
        START_YEAR, START_MONTH, START_DAY = request.args["START_YEAR"], request.args["START_MONTH"], request.args["START_DAY"]
        if(START_YEAR=="" and START_MONTH=="" and START_DAY==""):
            try:
                START_DATE = Transaction.query.order_by(Transaction.added_date).first().added_date
            except:
                abort(500)
        elif(START_YEAR!=None and START_MONTH!=None and START_DAY!=None):
            START_DATE = datetime.datetime(year=int(START_YEAR), month=int(START_MONTH), day=int(START_DAY), hour=0, minute=0, second=0)
        else:
            return jsonify({"error":"Invalid parameters provided. Either all are NULL or none are NULL"}), 400
    except:
        return jsonify({"error":"start Date not provided error in processing start date"}), 400
    try:
        END_YEAR, END_MONTH, END_DAY = request.args["END_YEAR"], request.args["END_MONTH"], request.args["END_DAY"]
        if(END_YEAR=="" and END_MONTH=="" and END_DAY==""):
            d = datetime.datetime.now()
            END_DATE = datetime.datetime(year=d.year, month=d.month, day=d.day, hour=23, minute=59, second=59, microsecond=999999)
        elif(END_YEAR!=None and END_MONTH!=None and END_DAY!=None):
            d = datetime.datetime.now()
            END_DATE = datetime.datetime(year=int(END_YEAR), month=int(END_MONTH), day=int(END_DAY), hour=23, minute=59, second=59, microsecond=999999)
        else:
            return jsonify({"error":"Invalid parameters provided. Either all are NULL or none are NULL"}), 400
    except:
        return jsonify({"error":"End Date not provided or error in processing end date"}), 400
    if END_DATE.date()>datetime.date.today():
        return jsonify({"error":"Invalid end date"}), 400
    try:
        usd_to_lbp_volume = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                                Transaction.usd_to_lbp == True).count()
        lbp_to_usd_volume = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                                Transaction.usd_to_lbp == False).count()
    except:
        abort(500)
    to_return = {
        "lbp_to_usd_volume":lbp_to_usd_volume,
        "usd_to_lbp_volume":usd_to_lbp_volume,
    }
    
    return jsonify(to_return), 200

