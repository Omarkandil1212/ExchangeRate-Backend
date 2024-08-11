from flask import abort, request, jsonify, Blueprint

from ..model.user import User
from ..app import bcrypt
from .utils import create_token

user_authentication = Blueprint('user_authentication', __name__)

#This route is inteneded to create a token for user authentication
@user_authentication.route('/', methods = ['POST'], strict_slashes=False)
def authenticate_user():
    try:
        user_name = request.json['user_name']
        password = request.json['password']
    except:
        abort(400)
    try:
        user = User.query.filter_by(user_name=user_name).first()
    except:
        abort(500)
    if(user is None):
        abort(403)
    if not(bcrypt.check_password_hash(user.hashed_password, password)):
        abort(403)
    token = create_token(user.id)
    return jsonify({"token":token}), 200
