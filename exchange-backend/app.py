from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from flask_mail import Mail
from .db_config import DB_CONFIG
import tensorflow as tf 
import joblib
import os
import logging

#I GOT THE CODE OF LOGGERS AND OS.environ from chatgpt to suppress the warnings i had

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
logging.getLogger('tensorflow').setLevel(50)

# Suppress scikit-learn warnings
logging.getLogger('sklearn').setLevel(50)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
app.config['MAIL_SERVER'] = 'smtp.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'xxxx'
app.config['MAIL_PASSWORD'] = 'xxxx'

CORS(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
socket = SocketIO(app, cors_allowed_origins="http://localhost:3000")
model = tf.keras.models.load_model('exchangeRateModel.h5')
mail = Mail(app)
scaler = joblib.load('scaler.pkl')
scaler_y = joblib.load('scaler_y.pkl')

SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"
 
from .API.User_Management import user_management
from .API.User_Authentication import user_authentication
from .API.Wallet_Management import wallet_management
from .API.Transaction_Management import transaction_management
from .API.Exchange_Rate_Management import exchange_rate_management
from .API.Statistics_Management import statistics_management
from .API.Predictions_Management import predictions_management
from .API.User_Transactions_Management import user_transaction_management
from .API.Notification_Management import notifications_management


app.register_blueprint(user_management, url_prefix='/user')
app.register_blueprint(user_authentication, url_prefix='/authentication')
app.register_blueprint(wallet_management, url_prefix='/wallet')
app.register_blueprint(transaction_management, url_prefix='/transaction')
app.register_blueprint(exchange_rate_management, url_prefix='/exchangeRate')
app.register_blueprint(statistics_management, url_prefix='/statistics')
app.register_blueprint(predictions_management, url_prefix='/predictions')
app.register_blueprint(user_transaction_management, url_prefix='/interUserTransactions')
app.register_blueprint(notifications_management, url_prefix='/notifications')

if __name__ == '__main__':
    app.run(debug=True)
