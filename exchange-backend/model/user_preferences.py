from ..app import db, ma

class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
    # Bounds preferences
    upper_bound_usd_to_lbp = db.Column(db.Float)
    lower_bound_usd_to_lbp = db.Column(db.Float)
    upper_bound_lbp_to_usd = db.Column(db.Float)
    lower_bound_lbp_to_usd = db.Column(db.Float)

    # Email preferences
    send_email = db.Column(db.Boolean)
    email = db.Column(db.String(128))

    # SMS preferences
    send_sms = db.Column(db.Boolean)
    phone_number = db.Column(db.String(128))
    def __init__(self, user_id, upper_bound_usd_to_lbp, lower_bound_usd_to_lbp, upper_bound_lbp_to_usd, lower_bound_lbp_to_usd, 
                 email, phone_number, send_email=False, send_sms=False):
        super(UserPreferences, self).__init__(user_id=user_id, upper_bound_usd_to_lbp = upper_bound_usd_to_lbp, 
                                              upper_bound_lbp_to_usd=upper_bound_lbp_to_usd, lower_bound_usd_to_lbp = lower_bound_usd_to_lbp,
                                              lower_bound_lbp_to_usd=lower_bound_lbp_to_usd, email=email, send_email=send_email,
                                              phone_number=phone_number, send_sms=send_sms)
    def __init__(self, user_id):
        super(UserPreferences, self).__init__(send_email=False, send_sms=False, user_id = user_id)

class UserPreferences_Schema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "upper_bound_usd_to_lbp", "lower_bound_usd_to_lbp", "upper_bound_lbp_to_usd", 
                  "lower_bound_lbp_to_usd","email","send_email","phone_number","send_sms")
        model = UserPreferences

user_preferences_schema = UserPreferences_Schema()
many_user_preferences_schema = UserPreferences_Schema(many=True)
