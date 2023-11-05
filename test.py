import unittest
from unittest.mock import patch

from adiserver.service import BlobDB
from adiserver.server import routeApp
from flask import Flask

# Importa Client para usar en el parche (mock)
from adiauthcli.client import Client
#from unittest.mock import patch, Mock
#from unittest.mock import MagicMock

class TestRouteApp(unittest.TestCase):
    
    def setUp(self):
        self.admin_token="3TjFh11wcaf9QZIuGibJi2dYNfU"
        self.client_test=Client("http://127.0.0.1:3001", check_service=False)
        self.client_test._admin_token_=self.admin_token
        self.app = Flask(__name__)
        self.BLOBDB = BlobDB('blob.db')
        routeApp(self.app, self.BLOBDB)

    def test_create_blob(self):
        
        self.client_test.new_user('Test1', 'create_blob')
        token_prueba=self.client_test.login('Test1', 'create_blob')
        
        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba}, json={'name': 'blob_anto', 'local_name': 'anto_blob1', 'visibility': 'private', 'users': 'antonio'})
            self.assertEqual(response.status_code, 201)

    def test_create_blob_invalid_user(self):
    
        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': 'Usuario no valido'}, json={'name': 'blob_test', 'local_name': 'local_test', 'visibility': 'private', 'users': 'test'})
            self.assertEqual(response.status_code, 401)

    def test_delete_blob(self):
    
        self.client_test.new_user('Test2', 'eliminar_blob')
        token_prueba=self.client_test.login('Test2', 'eliminar_blob')
        
        with self.app.test_client() as test_app:
            
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba}, json={'name': 'prueba_eliminar', 'local_name': 'anto_blob1', 'visibility': 'private', 'users': 'preuba2'})
            id_blob=response.text[0]
            response=test_app.delete('/api/v1/blob/'+id_blob, headers={'USER-TOKEN': token_prueba})
            
            self.assertEqual(response.status_code, 204)

    def test_delete_blob_invalidToken(self):
        
        self.client_test.new_user('Test2_1', 'eliminar_blob_invalid')
        token_prueba=self.client_test.login('Test2_1', 'eliminar_blob_invalid')
        
        with self.app.test_client() as test_app:
            
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba}, json={'name': 'prueba_eliminar', 'local_name': 'anto_blob1', 'visibility': 'private', 'users': 'prueba2'})
            id_blob=response.text[0]
            response=test_app.delete('/api/v1/blob/'+id_blob, headers={'USER-TOKEN': 'usuario-no-valido'})
            self.assertEqual(response.status_code, 401)

    def test_update_blob(self):
        
        self.client_test.new_user('Test3', 'actualizar_blob')
        token_prueba=self.client_test.login('Test3', 'actualizar_blob')
        
        with self.app.test_client() as test_app:
            
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba}, json={'name': 'prueba_actualizar', 'local_name': 'actualizar', 'visibility': 'private', 'users': 'test3'})
            id_blob=response.text[0]
            update_blob={
                            "name": "nuevo_nombre_del_blob",
                            "local_name": "local_blob1",
                            "visibility": "private",
                            "users": "raul"
                        }

            response=test_app.put('/api/v1/blob/'+id_blob, headers={'USER-TOKEN': token_prueba},data=update_blob)
            self.assertEqual(response.status_code, 204)

    def test_update_blob_invalidToken(self):
        
        self.client_test.new_user('Test3_2', 'actualizar_blob_invalid')
        token_prueba=self.client_test.login('Test3_2', 'actualizar_blob_invalid')
        
        with self.app.test_client() as test_app:
            
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba}, json={'name': 'prueba_actualizar', 'local_name': 'actualizar', 'visibility': 'private', 'users': 'test3'})
            id_blob=response.text[0]
            update_blob={
                            "name": "nuevo_nombre_del_blob",
                            "local_name": "local_blob1",
                            "visibility": "private",
                            "users": "raul"
                        }

            response=test_app.put('/api/v1/blob/'+id_blob, headers={'USER-TOKEN': 'usuario-no-valido'},data=update_blob)
            self.assertEqual(response.status_code, 401)
            
    def test_update_blob_visibility(self):
        self.client_test.new_user('Test4', 'actualizar_blob_visibility')
        token_prueba = self.client_test.login('Test4', 'actualizar_blob_visibility')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_actualizar', 'local_name': 'actualizar', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            update_data = {
                "visibility": "public"
            }

            response = test_app.put('/api/v1/blob/' + str(id_blob) + '/visibility',
                                    headers={'USER-TOKEN': token_prueba}, json=update_data)
            self.assertEqual(response.status_code, 204)

    def test_update_blob_visibility_invalidToken(self):
        self.client_test.new_user('Test4_2', 'actualizar_blob_visibility_invalid')
        token_prueba = self.client_test.login('Test4_2', 'actualizar_blob_visibility_invalid')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_actualizar', 'local_name': 'actualizar', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            update_data = {
                "visibility": "public"
            }

            response = test_app.put('/api/v1/blob/' + str(id_blob) + '/visibility',
                                    headers={'USER-TOKEN': 'usuario-no-valido'}, json=update_data)
            self.assertEqual(response.status_code, 401)

    def test_get_myBlobs(self):
        self.client_test.new_user('Test5', 'obtenerMyBlobs')
        token_prueba = self.client_test.login('Test5', 'obtenerMyBlobs')

        with self.app.test_client() as test_app:
            response = test_app.get('/api/v1/blob/myblobs', headers={'USER-TOKEN': token_prueba})
            self.assertEqual(response.status_code, 200)

    def test_create_blob_acl(self):
        self.client_test.new_user('Test3', 'acl')
        token_prueba = self.client_test.login('Test3', 'acl')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_acl', 'local_name': 'acl', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            acl_data = {
                "user": "raul"
            }

            response = test_app.post('/api/v1/blob/' + str(id_blob) + '/acl', headers={'USER-TOKEN': token_prueba},
                                    json=acl_data)
            self.assertEqual(response.status_code, 204)

    def test_delete_blob_acl(self):
        self.client_test.new_user('Test3', 'acl')
        token_prueba = self.client_test.login('Test3', 'acl')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_acl', 'local_name': 'acl', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            acl_data = {
                "user": "raul"
            }

            test_app.post('/api/v1/blob/' + str(id_blob) + '/acl', headers={'USER-TOKEN': token_prueba}, json=acl_data)
            response = test_app.delete('/api/v1/blob/' + str(id_blob) + '/acl/raul', headers={'USER-TOKEN': token_prueba})
            self.assertEqual(response.status_code, 201)

    def test_update_blob_acl(self):
        self.client_test.new_user('Test3', 'acl')
        token_prueba = self.client_test.login('Test3', 'acl')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_acl', 'local_name': 'acl', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            acl_data = {
                "user": "raul"
            }

            response = test_app.put('/api/v1/blob/' + str(id_blob) + '/acl', headers={'USER-TOKEN': token_prueba},
                                    json=acl_data)
            self.assertEqual(response.status_code, 204)

    def test_get_blob_acl(self):
        self.client_test.new_user('Test3', 'acl')
        token_prueba = self.client_test.login('Test3', 'acl')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_acl', 'local_name': 'acl', 'visibility': 'private',
                                          'users': 'test3'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            acl_data = {
                "user": "raul"
            }

            test_app.post('/api/v1/blob/' + str(id_blob) + '/acl', headers={'USER-TOKEN': token_prueba}, json=acl_data)
            response = test_app.get('/api/v1/blob/' + str(id_blob) + '/acl', headers={'USER-TOKEN': token_prueba})
            self.assertEqual(response.status_code, 200)

    def test_get_blob_hash(self):
        self.client_test.new_user('Test3', 'hash')
        token_prueba = self.client_test.login('Test3', 'hash')

        with self.app.test_client() as test_app:
            response = test_app.post('/api/v1/blob', headers={'USER-TOKEN': token_prueba},
                                    json={'name': 'prueba_hash', 'local_name': 'hash', 'visibility': 'private', 'users': 'test3', 'data': 'This is a test data for hash calculation'})
            #id_blob = response.json['BlobId']
            id_blob=response.text[0]
            response = test_app.get('/api/v1/blob/' + str(id_blob) + '/hash?type=MD5', headers={'USER-TOKEN': token_prueba})
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
