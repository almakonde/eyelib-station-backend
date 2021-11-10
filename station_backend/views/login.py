import jwt, json
from datetime import datetime, timedelta

from flask import Flask, request, make_response, session, jsonify
from werkzeug.security import check_password_hash
from mjk_backend.restful import Restful
from station_backend.settings import load as load_settings


settings = load_settings()
secret_key = settings.secretKey
passwd = {
    'admin': {
        'password': 'sha256$bemYnOoI$3ecaa2bfb25354a9a18c1365e9e4ffea86751377ff6f11b20894f3f0bbdca286',
        'roles' : ['admin', 'tech', 'patient'],
    },
}

roles = {
    'admin': [
        'techFrontend',
        'patientList',
        'engineer',
        'roleModification',
        'examinationList',
        'roleCreation',
        'stationFrontend',
    ],
    'tech': ['techFrontend','patientList'],
    'patient': ['labRat'],
}

class LoginView(Restful):

    def __init__(self, app: Flask):
        super().__init__(app, 'login')

    def post(self, *args, **kwargs):
        print('/login got:\n\tJSON', request.json, '\n\tDATA', request.data)
        username = request.json.get('username', None)
        user = passwd.get(username)
        if user:
            password = request.json.get('password', None)
            role_list = user.get('roles')
            permissions = list({p for r in role_list for p in roles[r]})
            pwhash = user.get('password')
            if password and check_password_hash(pwhash, password):
                response = {
                    'message': 'Successfully logged in.',
                    'status': 'success',
                    'permissions' : permissions,
                    'roles' : role_list,
                    'token': encode_auth_token(username).decode(),
                    'user' : username,
                }
                print('/login returning', response)
                resp = make_response(jsonify(response))
                return resp, 200
        return "Login incorrect", 401

def encode_auth_token(username):
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=2),
            'iat': datetime.utcnow(),
            'sub': username
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')
    except Exception as e:
        return False

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, secret_key)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
