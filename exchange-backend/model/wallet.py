from ..app import db, ma

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    usd_amount = db.Column(db.Float, nullable = False)
    lbp_amount = db.Column(db.Float, nullable = False)
    
    def __init__(self, user_id, usd_amount, lbp_amount):
        super(Wallet, self).__init__(user_id = user_id, usd_amount=usd_amount, lbp_amount=lbp_amount)

class WalletSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "usd_amount", "lbp_amount")
        model = Wallet
        
wallet_schema = WalletSchema()