import functools
from flask import make_response, jsonify, session

def roles_required(*role_names):
    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            #if not session.get('rolePermissions'):
            #    responseObject = {
            #        'status': 'fail',
            #        'message': 'User is not logged in'
            #    }
            #    return make_response(jsonify(responseObject)), 401

            #rolePermissionArray = []

            #for rolePermission in session['rolePermissions']:
            #    rolePermissionArray.append(rolePermission)

            #missing_roles = [
            #    role_name
            #    for role_name in role_names
            #        if role_name not in rolePermissionArray
            #]

            #if missing_roles:
            #   responseObject = {
            #        'status': 'fail',
            #        'message': 'User is not permitted this action'
            #    }
            #    return make_response(jsonify(responseObject)), 401
            return original_route(*args, **kwargs)
        return decorated_route
    return decorator

def single_role_required(*role_names):
    def decorator(original_route):
        @functools.wraps(original_route)
        def decorated_route(*args, **kwargs):
            #if not session['rolePermissions']:
            #    responseObject = {
            #        'status': 'fail',
            #        'message': 'User is not logged in'
            #    }
             #   return make_response(jsonify(responseObject)), 401

            #rolePermissionArray = []

            #for rolePermission in session['rolePermissions']:
            #    rolePermissionArray.append(rolePermission)

            #permissionFound = True;

            #for role_name in role_names:
            #    if role_name in rolePermissionArray:
            #        permissionFound = True

            #if not permissionFound:
            #    responseObject = {
            #        'status': 'fail',
            #        'message': 'User is not permitted this action'
            #    }
             #   return make_response(jsonify(responseObject)), 401
            return original_route(*args, **kwargs)
        return decorated_route
    return decorator
