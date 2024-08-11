from ..app import db, ma

class UserSid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_sid_java = db.Column(db.String(256), nullable=True)
    user_sid_react = db.Column(db.String(256), nullable=True)
    user_sid_android = db.Column(db.String(256), nullable=True)
    def __init__(self, user_id):
        super(UserSid, self).__init__(user_id=user_id)
    
class UserSidSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_id", "user_sid_java", "user_sid_react", "user_sid_android")
        model = UserSid


user_sid_schema = UserSidSchema()