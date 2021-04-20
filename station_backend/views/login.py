import jwt, json

from station_backend.settings import load as load_settings
from flask import Flask, request, make_response,session
from mjk_backend.restful import Restful


settings = load_settings()
#secret_key = settings.secretKey


class LoginView(Restful):

    def __init__(self, app: Flask):
        super().__init__(app, 'login')

    def post(self, *args, **kwargs):
        rolePermission = request.json['roles']
        auth_token = request.json['token']
        userId = request.json['userId']


        if auth_token is not None:
            # We decoded the token here which will give us the user ID used in the encoding
            userIdFromToken = self.decode_auth_token(auth_token)
            if int(userId) == int(userIdFromToken):
                if rolePermission is not None:
                    rolePermissionPythonArray = json.loads(rolePermission)
                    session['rolePermissions'] = rolePermissionPythonArray
                    return "Logged in"
            else:
                return "Not logged in"




    def decode_auth_token(self,auth_token):
        try:
            payload = jwt.decode(auth_token, secret_key)
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
