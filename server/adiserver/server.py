#!/usr/bin/env python3

'''Blob server'''

import hashlib
import sys
import logging
import argparse 
import json

from flask import Flask, make_response, request

from adiserver import DEFAULT_PORT, HTTPS_DEBUG_MODE, DEFAULT_BLOB_DB
from adiserver.service import BlobDB
from adiauthcli.client import Client,Unauthorized,UserNotExists,UserAlreadyExists


def routeApp(app, BLOBDB):
    '''Enruta la API REST a la webapp'''

    @app.route('/api/v1/blob', methods=['POST'])
    def create_blob():
        '''Crea un nuevo blob'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        if "USER-TOKEN" in request.headers:
            try:
                user_token = request.headers["USER-TOKEN"]
                owner_blob= client.token_owner(user_token)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

            data = request.get_json()
            name = data['name']
            local_name = data['local_name']
            visibility = data['visibility']
            users = data['users']

            blobid = BLOBDB.create_blob(name, local_name, visibility, users,owner_blob)

            return make_response({'BlobId': blobid,"URLaccess":'/api/v1/blob/'+str(blobid)}, 201)
        else:
            return make_response('Unauthorized', 401)

    @app.route('/api/v1/blob/<blobId>', methods=['GET'])
    def get_blob(blobId):
        client = Client("http://127.0.0.1:3001", check_service=False)
        blob_visibility=BLOBDB.getVisibilityBlob(blobId)
        
        if blob_visibility == 'public':
            '''Obtiene un blob por su ID'''
            blob=BLOBDB.get_blob(blobId)
            
            response = {
                "id": blob[0],
                "name": blob[1],
                "local_name": blob[2],
                "visibility": blob[3],
                "users": [blob[4]]
            }
            response_json = json.dumps(response)

            return make_response(response_json,200)
        
        elif "USER-TOKEN" in request.headers:
                try:
                    user_token = request.headers["USER-TOKEN"]
                    user= client.token_owner(user_token)
                    owner = BLOBDB.blobOwner(blobId)
                    users=BLOBDB.get_users(blobId)
                    if user in users or owner == user:
                        blob=BLOBDB.get_blob(blobId)
                        
                        response = {
                            "id": blob[0],
                            "name": blob[1],
                            "local_name": blob[2],
                            "visibility": blob[3],
                            "users": [blob[4]]
                        }
                        response_json = json.dumps(response)
                        return make_response(response_json,200)
                    else:
                        return make_response('Unauthorized', 401)
                except Unauthorized as e:
                    return make_response('Unauthorized', 401)
                except UserNotExists as e:
                    return make_response('Unauthorized', 401)
        else:
            return make_response('Unauthorized', 401)
        
    @app.route('/api/v1/blob/<blobId>', methods=['DELETE'])
    def delete_blob(blobId):
        '''Elimina un blob por su ID'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                if user == None or owner != user or owner == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

            BLOBDB.delete_blob(blobId)
            return make_response({}, 204)
        else:
            return make_response('Unauthorized', 401)

    @app.route('/api/v1/blob/<blobId>', methods=['PUT'])
    def update_blob(blobId):
        '''Actualiza un blob por su ID'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                if user == None or owner != user or owner == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

            data = request.get_json()
            name = data['name']
            local_name = data['local_name']
            visibility = data['visibility']
            users = data['users']

            BLOBDB.update_blob(blobId, name, local_name, visibility, users)
            return make_response({}, 204)
        else:
            return make_response('Unauthorized', 401)
        
    @app.route('/api/v1/blob/<blobId>/visibility', methods=['PUT', 'PATCH'])
    def update_blob_visibility(blobId):
        '''Actualiza la visibilidad de un blol por su ID'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                if user == None or owner != user or owner == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

            data = request.get_json()
            visibility = data['visibility']
            if visibility == "True":
                visibility = 'public'
            else:
                visibility = 'private'
            BLOBDB.change_visibility(blobId, visibility)

            return make_response({},204)
        else:
            return make_response('Unauthorized', 401)
    
    @app.route('/api/v1/blob/myblobs', methods=['GET'])
    def get_myBlobs():
        '''Obtiene todos los blobs un usuario determinado si es el propietario'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                if user == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)
        
            user_blobs = BLOBDB.get_blobs_by_user(user)
            return make_response(user_blobs, 200)
        else:
            return make_response('Unauthorized', 401)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['POST'])
    def create_blob_acl(blobId):
        '''Crea la acl de un blob'''
        client = Client("http://127.0.0.1:3001/", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                if user == None or owner != user or owner == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

        data = request.get_json()
        user_to_add_permission = data['user']

        blob = BLOBDB.get_blob(blobId)
        users_blob = list(BLOBDB.get_users(blobId))

        if blob == None:
            return make_response('Blob not found', 404)
        else:
            if user_to_add_permission in users_blob:
                print('User already has permission')
                return make_response('User already has permission', 409)
            else:
                users_blob.append(user_to_add_permission)
                print(users_blob)
                BLOBDB.update_blob(blob['name'], blob['local_name'], blob['visibility'], users_blob)
                return make_response({}, 204)

    @app.route('/api/v1/blob/<blobId>/acl/<username>', methods=['DELETE'])
    def delete_blob_acl(blobId,username):
        '''Elimina un usuario del acl de un blob'''
        client = Client("http://127.0.0.1:3001/", check_service=False)
        if "USER-TOKEN" in request.headers:
            
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                if user == None or owner != user or owner == None:
                    return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)

        blob = BLOBDB.get_blob(blobId)
        
        if blob == None:
            return make_response('Blob not found', 404)
        else:
            users_blob = list(BLOBDB.get_users(blobId))

            if username not in users_blob:
                print('User does not have permission')
                return make_response('User does not have permission', 409)
            else:
                BlobDB.delete_user(blobId, username)
                return make_response('User permission removed', 201)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['PUT, PATCH'])
    def update_blob_acl(blobId):
        '''Actualiza un ACL para un blob'''
        client = Client("http://127.0.0.1:3001/", check_service=False)
        if "USER-TOKEN" in request.headers:
            user_token = request.headers["USER-TOKEN"]
            user= client.token_owner(user_token)
            owner = BLOBDB.blobOwner(blobId)
            if user == None or owner != user or owner == None:
                return make_response('Unauthorized', 401)
        else:
            return make_response('Unauthorized', 401)

        data = request.get_json()

        user_to_add_permission = data['users']

        blob = BLOBDB.get_blob(blobId)
        users_blob = list(BLOBDB.get_users(blobId))

        if blob == None:
            return make_response('Blob not found', 404)
        else:
            if user_to_add_permission in users_blob:
                print('User already has permission')
                return make_response('User already has permission', 409)
            else:
                users_blob.append(user_to_add_permission)
                BLOBDB.update_blob(blobId, blob[1], blob[2], blob[3], user_to_add_permission)
                return make_response({}, 204)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['GET'])
    def get_blob_acl(blobId):
        '''Obtiene un ACL para un blob'''
        client = Client("http://127.0.0.1:3001/", check_service=False)
        if "USER-TOKEN" in request.headers:
            user_token = request.headers["USER-TOKEN"]
            user= client.token_owner(user_token)
            owner = BlobDB.blobOwner(blobId)
            if user == None or owner != user or owner == None:
                return make_response('Unauthorized', 401)
        else:
            return make_response('Unauthorized', 401)

        blob = BLOBDB.get_blob(blobId)

        if blob == None:
            return make_response('Blob not found', 404)
        else:
            acl_blob=list(BLOBDB.get_users(blobId))
        return make_response(acl_blob,200)

    @app.route('/api/v1/blob/<blobId>/hash', methods=['GET'])
    def get_blob_hash(blobId):
        '''Obtiene el hash de un blob por su ID'''
        client = Client("http://127.0.0.1:3001", check_service=False)
        blob_visibility=BLOBDB.getVisibilityBlob(blobId)
        
        if blob_visibility == 'public':
            hash_type = request.args.get('type')
            if hash_type == None:
                return make_response('You must to give a hash type (MD5, SHA256)', 400)
            else:
                hash_type = hash_type.upper()
                if hash_type != 'MD5' and hash_type != 'SHA256':
                    return make_response('Hash type not valid', 400)
                else:
                    blob = BLOBDB.get_blob(blobId)
                    #print(blob)
                    #print(blob[1])
                    if blob == None:
                        return make_response('Blob not found', 404)
                    else:
                        # Para concatenar todos los elementos del objeto 'blob' en una sola cadena
                        blob_data = ''.join(map(str, blob)).encode('utf-8')
                        if hash_type == 'MD5':
                            sum_hash = hashlib.md5(blob_data).hexdigest()
                        elif hash_type == 'SHA256':
                            sum_hash = hashlib.sha256(blob_data).hexdigest()
            return make_response(sum_hash, 200)
        elif "USER-TOKEN" in request.headers:
            try:
                user_token = request.headers["USER-TOKEN"]
                user= client.token_owner(user_token)
                owner = BLOBDB.blobOwner(blobId)
                users=BLOBDB.get_users(blobId)
                if user in users or owner == user:
                    hash_type = request.args.get('type')
                    if hash_type == None:
                        return make_response('You must to give a hash type (MD5, SHA256)', 400)
                    else:
                        hash_type = hash_type.upper()
                        if hash_type != 'MD5' and hash_type != 'SHA256':
                            return make_response('Hash type not valid', 400)
                        else:
                            blob = BLOBDB.get_blob(blobId)
                            #print(blob)
                            #print(blob[1])
                            if blob == None:
                                return make_response('Blob not found', 404)
                            else:
                                # Para concatenar todos los elementos del objeto 'blob' en una sola cadena
                                blob_data = ''.join(map(str, blob)).encode('utf-8')
                                if hash_type == 'MD5':
                                    sum_hash = hashlib.md5(blob_data).hexdigest()
                                elif hash_type == 'SHA256':
                                    sum_hash = hashlib.sha256(blob_data).hexdigest()
                    return make_response(sum_hash, 200)
                else:
                        return make_response('Unauthorized', 401)
            except Unauthorized as e:
                return make_response('Unauthorized', 401)
            except UserNotExists as e:
                return make_response('Unauthorized', 401)
        else:
            return make_response('Unauthorized', 401)

def main():
    '''Entry point for the auth server'''
    user_options = parse_commandline()

    service = ServerService(user_options.db_path, user_options.address, user_options.port)

    try:
        print(f'Starting service on: {service.base_uri}')
        service.start()
    except Exception as error: # pylint: disable=broad-except
        logging.error('Cannot start API: %s', error)
        sys.exit(2)

    service.stop()


class ServerService:
    '''Wrap all components used by the service'''
    def __init__(self, db_path, host='0.0.0.0', port=DEFAULT_PORT):
        self._blobdb_ = BlobDB(db_path)

        self._host_ = host
        self._port_ = port

        self._app_ = Flask(__name__.split('.', maxsplit=1)[0])
        routeApp(self._app_, self._blobdb_)

    @property
    def base_uri(self):
        '''Get the base URI to access the API'''
        host = '127.0.0.1' if self._host_ in ['0.0.0.0'] else self._host_
        return f'http://{host}:{self._port_}'

    def start(self):
        '''Start HTTP server'''
        self._app_.run(host=self._host_, port=self._port_, debug=HTTPS_DEBUG_MODE)

    def stop(self):
        '''Cancel all remaining timers'''

def parse_commandline():
    '''Parse command line'''
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        '-p', '--port', type=int, default=DEFAULT_PORT,
        help='Listening port (default: %(default)s)', dest='port'
    )
    parser.add_argument(
        '-l', '--listening', type=str, default='0.0.0.0',
        help='Listening address (default: all interfaces)', dest='address'
    )
    parser.add_argument(
        '-d', '--db', type=str, default=DEFAULT_BLOB_DB,
        help='Database to use (default: %(default)s', dest='db_path'
    )


    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
