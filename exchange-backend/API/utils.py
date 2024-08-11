from ..app import mail, app
from flask_mail import Message
from flask import jsonify
from ..model.transaction import Transaction
import datetime
import re
import jwt
import datetime
from ..app import SECRET_KEY

#This function sends the saame message to all users based on their prference (send_email ?= true or false)
def send_mails_to_users(user_preferences, message):
    with app.app_context(): 
        user_emails = []
        for user in user_preferences:
            if user['send_email'] and user['email']:
                user_emails.append(user['email'])
        msg = Message('Exchange Rate Update', sender='exchangerateapp430L@outlook.com', bcc=user_emails, body=message)
        try:
            mail.send(msg)
        except:
            return jsonify({"error": "Internal Error"}), 400

#This function sends a specific message to specific user email
def send_mails_to_multiple_users(email_messages):
    with app.app_context():
        for email, message in email_messages:
            msg = Message('Exchange Rate Alert', sender='exchangerateapp430L@outlook.com', recipients=[email], body=message)
            try:
                mail.send(msg)
            except Exception as e:
                return jsonify({"error": "Failed to send email, error: {}".format(str(e))}), 400

#This function gets the exchange rate of a specified date based on transactions in last 3 days
def get_exchange_rate(date):
    d = datetime.timedelta(hours = 72)
    END_DATE = date
    START_DATE = date - d
    USD_to_LBP_Values = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                              Transaction.usd_to_lbp == True).all()
    n = len(USD_to_LBP_Values)
    sum_Of_Rates = 0
    USD_to_LBP_rate = 0
    for i in range(n):
        rate = (USD_to_LBP_Values[i].lbp_amount/USD_to_LBP_Values[i].usd_amount)
        sum_Of_Rates += rate
    try:
        USD_to_LBP_rate = sum_Of_Rates/n
    except:
        USD_to_LBP_rate = None
    LBP_to_USD_Values = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),
                                              Transaction.usd_to_lbp == False).all()
    n = len(LBP_to_USD_Values)
    sum_Of_Rates = 0
    LBP_to_USD_rate = 0
    for i in range(n):
        rate = (LBP_to_USD_Values[i].lbp_amount/LBP_to_USD_Values[i].usd_amount)
        sum_Of_Rates += rate
    try:
        LBP_to_USD_rate = sum_Of_Rates/n
    except:
        LBP_to_USD_rate = None
    to_return = {"usd_to_lbp": USD_to_LBP_rate, "lbp_to_usd": LBP_to_USD_rate}
    return to_return

#This function calculate percentage change in a list between first and last number
def calculate_percentage_change(values):
    if len(values) < 2:
        return None
    return ((values[-1] - values[0]) / values[0]) * 100

#This function checks if a password has a special character. If not, it returns false. GPT helped with this function
def check_special_characters(password):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+={}\[\]:;"\'<>,.?\/\\-]).{8,}$', password)) and not(bool(re.search(r'\s', password)))

#This function checks if a username has a special character. If not, it returns true. GPT helped with this function
def check_special_characters_for_username(username):
    pattern = r'[!@#$%^&*()+={}\[\]:;"\'<>,.?\/\\-]'
    # Check if any match is found
    if re.search(pattern, username):
        return True
    else:
        return False

#This function checks if password length is greater than 7 and less than 129.
def check_password_length(password):
    return len(password)<=128 and len(password)>=8

#This function checks if password has certain unallowed and frequently used password and returns false if they exist
def check_for_patterns(password):
    common_patterns = [
        r'\b123\b',
        r'\b123456\b',
        r'\b987654\b',
        r'\bqwerty\b',
        r'\basdfgh\b',
        r'\bzxcvbn\b',
        r'\bpassword\b',
        r'\bletmein\b',
        r'\badmin\b',
        r'\bhello\b',
        r'\bmonkey\b',
        r'\b(\w+)\1\b'  # Matches repeating characters like "aaaaaa" or "111111"
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password, re.IGNORECASE):
            return False
    return True

#This function extracts the token from the header  
def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None

#This function decodes the token and checks if it is valid
def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['sub']

#This function creates a token for users to authenticate
def create_token(user_id):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=4),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
    )

#This function makes sure that the email provided is a valid one. 
def validate_email(email):  
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):  
        return True  
    return False  
