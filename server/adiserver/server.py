#!/usr/bin/env python3

'''Auth server'''


import sys
import logging
import argparse

from flask import Flask, make_response, request

from adiserver import DEFAULT_PORT, HTTPS_DEBUG_MODE, DEFAULT_BLOB_DB
from adiserver.service import BlobDB
from adiserver.client import Client



def routeApp(app, BLOBDB):
    '''Enruta la API REST a la webapp'''

    @app.route('/api/v1/blob', methods=['POST'])
    def create_blob():
        '''Crea un nuevo blob'''
        print("entra create blob")
        client = Client("http://127.0.0.1:3011", check_service=False)
        if "USER-TOKEN" in request.headers:
            user_token = request.headers["USER-TOKEN"]
            user= client.token_owner(user_token)
            print(user)
        else:
            print("no se mete")
            if user == None:
                return make_response('Unauthorized', 401)

        data = request.get_json()
        name = data['name']
        local_name = data['local_name']
        visibility = data['visibility']
        users = data['users']

        blobid = BLOBDB.create_blob(name, local_name, visibility, users)

        return make_response({'BlobId': blobid,"URLaccess":'/api/v1/blob/'+str(blobid)}, 201)

    @app.route('/api/v1/blob/<blobId>', methods=['GET'])
    def get_blob(blobId):
        '''Obtiene un blob por su ID'''

        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blob>', methods=['DELETE'])
    def delete_blob(blobId):
        '''Elimina un blob por su ID'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>', methods=['PUT'])
    def update_blob(blobId):
        '''Actualiza un blob por su ID'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/hash', methods=['GET'])
    def get_blob_hash(blobId):
        '''Obtiene el hash de un blob por su ID'''
        type_param = request.args.get('type')
        if type != 'HASH':
            return make_response('Invalid type param', 400)

        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/visibility', methods=['PUT, PATCH'])
    def update_blob_visibility(blobId):
        '''Actualiza la visibilidad de un blob por su ID'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['POST'])
    def create_blob_acl(blobId):
        '''Crea un ACL para un blob'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['PUT, PATCH'])
    def update_blob_acl(blobId):
        '''Actualiza un ACL para un blob'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/acl', methods=['GET'])
    def get_blob_acl(blobId):
        '''Obtiene un ACL para un blob'''
        return make_response('Not implemented', 501)

    @app.route('/api/v1/blob/<blobId>/acl/<username>', methods=['DELETE'])
    def delete_blob_acl(blobId, username):
        '''Elimina un ACL para un blob'''
        return make_response('Not implemented', 501)


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