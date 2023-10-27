#!/usr/bin/env python3

import os.path
import tempfile
import unittest
from pathlib import Path

from adiauth.errors import Unauthorized, ObjectAlreadyExists, ObjectNotFound
from adiauth import ADMIN

from adiauth.service import AuthDB, TokenManager


ADMIN_TOKEN = 'test_admin_token'
WRONG_TOKEN = 'this_token_should_not_exists'
USER1 = 'test_user1'
USER2 = 'test_user2'
HASH1 = 'test_user1_hash'
NEW_HASH1 = 'test_user1_hash_new'
WRONG_HASH1 = 'test_user1_hash_but_wrong'


class TestPersistentDB(unittest.TestCase):

    def test_creation(self):
        '''Test initialization'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            self.assertFalse(os.path.exists(dbfile))
            authdb = AuthDB(db_file=dbfile)
            self.assertTrue(os.path.exists(dbfile))
            self.assertTrue(authdb.exists(ADMIN))

    def test_create_user(self):
        '''Test create user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            self.assertFalse(authdb.validHash(HASH1, USER1))
            self.assertFalse(authdb.exists(USER1))
            authdb.newUser(USER1, HASH1)
            self.assertTrue(authdb.validHash(HASH1, USER1))
            self.assertTrue(authdb.exists(USER1))

    def test_create_admin_user(self):
        '''Test create admin'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            with self.assertRaises(ObjectAlreadyExists):
                authdb.newUser(ADMIN, HASH1)

    def test_create_duplicated_user(self):
        '''Test create añready-exists user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            authdb.newUser(USER1, HASH1)
            with self.assertRaises(ObjectAlreadyExists):
                authdb.newUser(USER1, HASH1)

    def test_removeUser(self):
        '''Test remove user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            authdb.newUser(USER1, HASH1)
            self.assertTrue(authdb.validHash(HASH1, USER1))
            self.assertTrue(authdb.exists(USER1))
            authdb.removeUser(USER1)
            self.assertFalse(authdb.validHash(HASH1, USER1))
            self.assertFalse(authdb.exists(USER1))

    def test_removeUser_with_token(self):
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            tokenman = TokenManager(ADMIN_TOKEN, authdb)

            authdb.newUser(USER1, HASH1)
            token = tokenman.newToken(USER1, HASH1)

            authdb.removeUser(USER1)
            with self.assertRaises(ObjectNotFound):
                tokenman.ownerOf(token)

    def test_remove_not_exists_user(self):
        '''Test remove not-exists user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            with self.assertRaises(ObjectNotFound):
                authdb.removeUser(USER1)

    def test_change_user_hash(self):
        '''Test change password hash of an user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            authdb.newUser(USER1, HASH1)
            self.assertTrue(authdb.validHash(HASH1, USER1))
            authdb.changePasswordHash(USER1, NEW_HASH1)
            self.assertFalse(authdb.validHash(HASH1, USER1))
            self.assertTrue(authdb.validHash(NEW_HASH1, USER1))

    def test_change_wrong_user_hash(self):
        '''Test change password hash of a wrong user'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            with self.assertRaises(ObjectNotFound):
                authdb.changePasswordHash(USER1, NEW_HASH1)

    def test_validHash_of_admin(self):
        '''Test check valid hash of admin'''
        class TokenManagerMock:
            admin_token = ADMIN_TOKEN
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            authdb.token_manager = TokenManagerMock()

            self.assertTrue(authdb.validHash(ADMIN_TOKEN, ADMIN))

    def test_exists_admin_user(self):
        '''Test check if admin user exists'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)

            self.assertTrue(authdb.exists(ADMIN))


class TestTokenManager(unittest.TestCase):

    def test_creation(self):
        '''Test creation of a new TokenManager()'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            tokenman = TokenManager(ADMIN_TOKEN, authdb)

            self.assertIs(authdb.token_manager, tokenman)
            self.assertEqual(ADMIN_TOKEN, tokenman.admin_token)
            tokenman.stop()

    def test_newToken(self):
        '''Test creation of a new token'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            tokenman = TokenManager(ADMIN_TOKEN, authdb)

            authdb.newUser(USER1, HASH1)

            token = tokenman.newToken(USER1, HASH1)
            self.assertEqual(USER1, tokenman.ownerOf(token))

            tokenman.stop()

    def test_newToken_wrong_hash(self):
        '''Test creation of a new token with wrong hash'''
        with tempfile.TemporaryDirectory() as workspace:
            dbfile = Path(workspace).joinpath('dbfile.json')
            authdb = AuthDB(db_file=dbfile)
            tokenman = TokenManager(ADMIN_TOKEN, authdb)

            authdb.newUser(USER1, HASH1)

            with self.assertRaises(Unauthorized):
                token = tokenman.newToken(USER1, WRONG_HASH1)

            tokenman.stop()
