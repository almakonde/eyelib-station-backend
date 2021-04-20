import jwt

from flask import Flask, session
from mjk_backend.restful import Restful

from station_backend.utilities.decoraters import roles_required



class LogoutView(Restful):

    def __init__(self, app: Flask):
        super().__init__(app, 'logout')

    def get(self, *args, **kwargs):
        print("Removing session")
        session.pop('rolePermissions', None)
        return "Logged out"

