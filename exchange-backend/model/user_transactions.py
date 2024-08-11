import datetime
from ..app import db, ma

class UserTransactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usd_amount = db.Column(db.Float, nullable=False)
    lbp_amount = db.Column(db.Float, nullable=False)
    usd_to_lbp = db.Column(db.Boolean, nullable=False)
    added_date = db.Column(db.DateTime)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    accepted = db.Column(db.Boolean, nullable=False)
    date_accepted = db.Column(db.DateTime)
    def __init__(self, usd_amount, lbp_amount, usd_to_lbp, user1_id):
        super(UserTransactions, self).__init__(usd_amount=usd_amount,
                                        lbp_amount=lbp_amount, usd_to_lbp=usd_to_lbp,
                                        added_date=datetime.datetime.now(),
                                        user1_id=user1_id,
                                        accepted = False
                                        )


class UserTransactionsSchema(ma.Schema):
    class Meta:
        fields = ("id", "usd_amount", "lbp_amount", "usd_to_lbp", "added_date", "user1_id", "user2_id", "accepted", "date_accepted")
        model = UserTransactions

user_transactions_schema = UserTransactionsSchema()
many_user_transactions_schema = UserTransactionsSchema(many=True)