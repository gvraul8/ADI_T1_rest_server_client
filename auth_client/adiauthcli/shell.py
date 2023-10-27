#!/usr/bin/env python3

import cmd
import getpass
import logging

from adiauthcli.client import Client

__version__ = '1.0'

_COMMENT_TAG_ = '#'


class Shell(cmd.Cmd):
    '''CMD shell implementation'''
    admin_token = None
    prompt = ''
    stop_on_error = True
    bad_exit = False
    interactive = True
    line_no = 0
    error_cause = 'Unknown error, see logs'

    _auth_ = None

    @property
    def interrupted(self):
        if self.stop_on_error:
            self.bad_exit = True
            return True
        return None

    @property
    def client(self):
        return self._auth_

    @client.setter
    def client(self, new_client: Client):
        self._auth_ = new_client
        self.__select_prompt__()

    def output(self, out: str):
        logging.debug(out)
        print(out)

    def preloop(self) -> None:
        self.__select_prompt__()
        return super().preloop()

    def precmd(self, line: str) -> str:
        self.line_no += 1
        self.__select_prompt__()
        cleanLine = line.strip()
        if cleanLine.startswith(_COMMENT_TAG_):
            return ""
        return super().precmd(line)

    def postcmd(self, stop: bool, line: str) -> bool:
        self.__select_prompt__()
        return super().postcmd(stop, line)

    def __select_prompt__(self):
        self.prompt = ''
        if self.interactive:
            self.prompt = 'ADI-Auth'
            if self.client is not None:
                if self.client.administrator:
                    self.prompt += '(admin)'
                elif self.client.logged:
                    self.prompt += '(user)'
                else:
                    self.prompt += '(offline)'
            self.prompt += ': '

    def default(self, line: str) -> None:
        self.output(f'*** Unknown syntax: {line}')
        return self.stop_on_error

    def emptyline(self) -> bool:
        pass

    def do_connect_to(self, line):
        '''Set the service URI'''
        if self.client is None:
            logging.debug('Setting client URL to: ', line)
            self.client = Client(line, admin_token=self.admin_token)
            return
        self.output(f'*** Client already connected. disconnect first!')
        return self.stop_on_error

    def do_disconnect(self, line):
        '''Unset the service URI'''
        if self.client is None:
            self.output('*** Client already disconnected, connect first!')
            return self.stop_on_error
        logging.debug('Unsetting client URL')
        if self.client.logged:
            self.client.logout()
        self.client = None

    def do_set_admin_token(self, line):
        '''Set the administrator token'''
        if self.client is None:
            self.admin_token = None if not line else line
            return
        self.output('*** Cannot change admin token while connected')
        return self.stop_on_error

    def do_new_user(self, line):
        '''Request to create a new user'''
        if not self.client:
            logging.error('Client is not connect, connect first')
            return self.stop_on_error
        if not self.client.administrator:
            logging.error('This command is only for administrators')
            return self.stop_on_error
        line = line.strip().split()
        if len(line) == 0:
            username = prompt_string('Enter username: ')
            password = prompt_password()
        elif len(line) == 1:
            username = line[0]
            password = prompt_password()
        elif len(line) == 2:
            username, password = line
        else:
            logging.error('new_user takes two optional argumens only')
            return self.stop_on_error
        try:
            self.client.new_user(username, password)
        except Exception as error:
            logging.error(f'Cannot create new user: {error}')
            return self.stop_on_error

    def do_delete_user(self, line):
        '''Request to remove a user'''
        if not self.client:
            logging.error('Client is not connect, connect first')
            return self.stop_on_error
        if not self.client.administrator:
            logging.error('This command is only for administrators')
            return self.stop_on_error
        if not line:
            username = prompt_string('Enter username: ')
        else:
            username = line.strip()
        try:
            self.client.delete_user(username)
        except Exception as error:
            logging.error(f'Cannot remove user: {error}')
            return self.stop_on_error

    def do_login(self, line):
        '''Get a user token'''
        if not self.client:
            logging.error('No connected to an Auth service, connect first')
            return self.stop_on_error
        if self.admin_token:
            logging.error('Session configured as administrator, unset admin token first')
            return self.stop_on_error
        if self.client.logged:
            logging.error('Already logged, logout first')
            return self.stop_on_error
        line = line.strip().split()
        if len(line) == 0:
            username = prompt_string('Enter username: ')
            password = prompt_password(confirm_password=False)
        elif len(line) == 1:
            username = line[0]
            password = prompt_password(confirm_password=False)
        elif len(line) == 2:
            username, password = line
        else:
            logging.error('new_user takes two optional argumens only')
            return self.stop_on_error
        try:
            self.client.login(username, password)
        except Exception as error:
            logging.error(f'Cannot create new user: {error}')
            return self.stop_on_error

    def do_logout(self, line):
        '''Logout client instance'''
        if not self.client:
            logging.error('No connected to an Auth service, connect first')
            return self.stop_on_error
        if self.admin_token:
            logging.error('Session configured as administrator, unset admin token first')
            return self.stop_on_error
        if not self.client.logged:
            logging.error('Already logged out, login first')
            return self.stop_on_error
        try:
            self.client.logout()
        except Exception as error:
            logging.error(f'Cannot logout: {error}')
            return self.stop_on_error

    def do_show_token(self, line):
        '''Show current auth token (user only)'''
        if not self.client:
            logging.error('Not connected to an Auth service, connect first')
            return self.stop_on_error
        if not self.client.logged:
            logging.error('Token is only available when logged in')
            return self.stop_on_error
        self.output(self.client.auth_token)

    def do_refresh_auth_token(self, line):
        '''Revoke current token and get new one'''
        '''Show current auth token (user only)'''
        if not self.client:
            logging.error('Not connected to an Auth service, connect first')
            return self.stop_on_error
        if not self.client.logged:
            logging.error('Refresh token requires login')
            return self.stop_on_error
        self.client.refresh_token()

    def do_EOF(self, line):
        '''Disconnect and quit'''
        return self.do_quit(line)

    def do_quit(self, line):
        '''Disconnect and quit'''
        if self.client is not None:
            if self.client.logged:
                self.client.logout()
        return True

    def help_connect_to(self):
        self.output('''Usage:
\tconnect_to <API_uri>
Instance new ADI Auth client with the given URL.''')

    def help_disconnect(self):
        self.output('''Usage:
\tdisconnect
Delete current client instance.''')

    def help_set_admin_token(self):
        self.output('''Usage:
\tset_admin_token [<ADMIN TOKEN>]
Set (or unset) the administrator token''')

    def help_new_user(self):
        self.output('''Usage:
\tnew_user [<USERNAME> [<PASSWORD>]]
Create new user. If some argument is missing, it will be requested interactively''')

    def help_delete_user(self):
        self.output('''Usage:
\tdelete_user [<USERNAME>]
Remove a single user. If USERNAME is missing, it will be requested interactively''')

    def help_quit(self):
        self.output('''Usage:
\tquit
Disconnects and close the shell.''')


def prompt_string(message) -> str:
    '''Ask user for something'''
    try:
        return input(message)
    except KeyboardInterrupt as error:
        logging.error('User cancel interactive prompt')
        raise error


def prompt_password(confirm_password=True) -> str:
    '''Ask user for a password'''
    while True:
        try:
            password = getpass.getpass()
            if not confirm_password:
                return password
            repeat_password = getpass.getpass('Repeat password: ')
        except KeyboardInterrupt as error:
            logging.error('User cancel interactive prompt')
            raise error
        if password == repeat_password:
            return password
        logging.error('Passwords does not match!')