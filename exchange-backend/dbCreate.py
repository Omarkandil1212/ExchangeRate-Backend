app_module = __import__('exchange-backend-sharafeddines.app', fromlist=['app', 'db'])
user_transactions_module = __import__('exchange-backend-sharafeddines.model.user_transactions', fromlist=['UserTransactions'])
user_module = __import__('exchange-backend-sharafeddines.model.user', fromlist=['User'])
transaction_module = __import__('exchange-backend-sharafeddines.model.transaction', fromlist=['Transaction'])
user_preferences_module = __import__('exchange-backend-sharafeddines.model.user_preferences', fromlist=['UserPreferences'])
wallet_module = __import__('exchange-backend-sharafeddines.model.wallet', fromlist=['Wallet'])
user_sid_module = __import__('exchange-backend-sharafeddines.model.user_sid', fromlist=['UserSid'])

db = app_module.db
UserTransactions = user_transactions_module.UserTransactions
User = user_module.User
Transaction = transaction_module.Transaction
User_Preferences = user_preferences_module.User_Preferences
Wallet = wallet_module.Wallet
UserSid = user_sid_module.UserSid

db.create_all()
