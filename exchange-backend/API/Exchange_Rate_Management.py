import datetime

from flask import jsonify, Blueprint, request, abort
from ..model.transaction import Transaction
from .utils import get_exchange_rate

exchange_rate_management = Blueprint('exchange_rate_management', __name__)

#This functions gets the exchange rate for this period in time based on last 3 days of transactions
@exchange_rate_management.route('/', methods = ['GET'], strict_slashes=False)
def calculate_exchange_rate():
    date = datetime.datetime.now()
    to_return = get_exchange_rate(date)
    return jsonify(to_return), 200

#This functions gets the exchange rate for every day in a date range in time based on last 3 days of transactions for each day
@exchange_rate_management.route('/withDates', methods = ['GET'])
def get_exchange_rates():
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
    to_return = []
    date = datetime.datetime(year=START_DATE.year, month=START_DATE.month, day=START_DATE.day, hour=23, minute=59, second=59, microsecond=999999)
    while date<=END_DATE:
        exchangeRates = get_exchange_rate(date)
        exchangeRates["date"] = date.strftime('%d-%m-%Y')
        to_return.append(exchangeRates)
        date += datetime.timedelta(days=1)
    return to_return,200