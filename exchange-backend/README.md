# Exchange Rate API
The Exchange Rate API is a RESTful web service that offers users current exchange rates and statistics. It also allows users to carry out transactions and monitor their history. This API is developed using Python and Flask, and it follows the OpenAPI v3.1.0 Specification for documentation.

# Features
- User authentication and registration
- Fetch the USD to LBP and LBP to USD rates
- Add real time transactions
- Add transactions for other users to accept if the amount in their wallets permits
- Get exchange rates between 2 specified dates
- Get statistics of rates between 2 specified dates
- Integration of ANN model to predict the exchange rate at a specific date
- Send notifications and emails (if specified) for users when exchange rate increases/decreases by 10%
- Send notifications and emails (if specified) for specific users when exchange rates meets their specified bounds (upper/lower bounds on exchange rate)

# Running the app
The following is intended to help you in installing all needed files to run the app on your machine.

## Prerequisites
- Have python 3.10 or later running on your machine
- Pip (install python packages)
- Virtual Environment

## Running Steps
- Start by cloning the repo on your machine:
`git clone https://github.com/EECE-430L/exchange-backend-sharafeddines.git`
- Then, create a file called `db_config.py` in `exchange-backend-sharafeddines` and include in it the path to your database
- After, open a terminal in `exchange-backend-sharafeddines.git` 
- (Optional) Create a virtual environment for your python and activate it:
On Windows: 
`py -3 -m venv venv`
`venv\Scripts\activate`
On Unix:
`python3 -m venv venv`
`. venv/bin/activate`
- After that, download all required packages by executing the command:
`pip install -r requirements.txt`
- Then, open a flask shell by executing `flask shell` and execute the following commands to create the tables in the database:
`app_module  =  __import__('exchange-backend-sharafeddines.app',  fromlist=['app',  'db'])`
`db  =  app_module.db`
`db.create_all()`
- Run the backend server:
`flask run`

The server will run on [http://127.0.0.1:5000/](http://localhost:5000/) and will be accessible accordingly
 
 # Socket Implementation
 - The server uses a socket specifically socket.io to send notifications.
 - There is a socketio at address [http://127.0.0.1:5000](http://localhost:5000) that users can connect to.
 - This socket sends notifications under the event `notification`. Listenning under this event will deliver the general notifications for you. They will be send in a json of the format `{"Title": title, "Message":message }`
 - To connect a specific user to the socket and allow him to receive notifications, the user should send his token to the socket. There are 3 events at which the socket server is listening and can save the sid of a specific user to send him specific notifications:
 -1. `send_token_java`: used for java fx applications
 -2. `send_token_android`: used for android applications
 -3. `send_token_react`: used for react applications
 All above events are listened to by the server. The message of each of the above events should be **only the token** of the user. The token can be null. Once the server receives and decodes the token, it saves the sid of the user in a database
 - Now, when the server sends specific notifications, it uses the sid of each user and emits on the event `notification`.
 - When users logout, they should not receive user specific notifications anymore. So, we have to remove the sid of each user. To do so, the socket is listening for 3 events to remove the sid of a specific user to stop sending him notifications:
  -1. `remove_sid_java`: used for java fx applications
 -2. `remove_sid_android`: used for android applications
 -3. `remove_sid_react`: used for react applications
All above events are listened to by the server. The message of each of the above events should be **only the token** of the user. The token can be null. Once the server receives and decodes the token, it removes the sid of the user in a database
- Use the event `send_token_...` on app open, user login, and user register to send the token of a user to the server
- Use the event `remove_sid_...` on user logout. Note that you have to  send the token in `remove_sid_...` before deleting the token