# coding: utf-8
from __future__ import (absolute_import, division, print_function, unicode_literals)
import logging
import os

import suds
from suds.plugin import MessagePlugin
from suds.client import Client


logging.basicConfig(level=logging.ERROR)
logging.getLogger('suds.client').setLevel(logging.ERROR)


class LoginError(Exception): pass


class MyPlugin(MessagePlugin):
    def prune(self, env):
        ignore_list = ['getActivityLogSubjects']
        pruned = []
        for i, c in enumerate(env.children):
            # print(i, c)
            if not (any(s in str(c) for s in ignore_list)):
                c.prune()
                if c.isempty(False):
                    pruned.append(c)
        for p in pruned:
            env.children.remove(p)

        return env

    def marshalled(self, context):
        context.envelope = self.prune(context.envelope)

        # def sending(self, context):
        # print(str(context.envelope))
        # def received(self, context):
        #     print(str(context.reply))


class BenefitPoint(object):
    """ Simple class for pragmatic access to the BenefitPoint
        Web Services through python.

        :param username: Username to login to Benefit Point
        :param password: Password to login to Benefit Point

        Usage:
            from webservices import webservices
            bp = webservices.BenefitPoint(username='you@me.net', password='password')
            ## Create the complex type to pass into the method
            accountsearch = bp.create_type('ns1:AccountSearchCriteria')
            accountsearch.active = True

            ## Call the method and pass in the type
            accounts = bp.call('findAccounts', accountsearch)
            print(accounts)

        Returns:
            BenefitPoint object

    """

    SESSION_FILE = os.path.join("c:/", "Temp", "benefitpoint_sessionid.txt")

    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            f.write('')

    def __init__(self, username='', password=''):
        self.sessionID = ''

        self.LOGIN_WSDL = str('https://www1.benefitpoint.com/aptusConnect/LoginV2.wsdl')
        self.BROKER_CONNECTV4 = str('https://www1.benefitpoint.com/aptusConnect/BrokerConnectV4.wsdl')

        self.login_client = Client(self.LOGIN_WSDL, plugins=[MyPlugin()])
        self.client = Client(self.BROKER_CONNECTV4, plugins=[MyPlugin()])

        self.username = username
        self.password = password


    def verify_login(self):
        ''' Login method to authenticate with Benefit Point.
            :param username: Username to login to Benefit Point
            :param password: Password to login to Benefit Point

            Returns:
                Session key to use in each future request.

        '''

        try:
            with open(self.SESSION_FILE, 'rt') as file:
                self.sessionID = file.read()

        except:
            pass

        if self.sessionID:
            token = self.client.factory.create('SessionIdHeader')
            token.sessionId = self.sessionID
            self.client.set_options(soapheaders=token)
            current_user = self.login_client.service.echo(self.sessionID)
            if self.sessionID == current_user:
                return

        else:
            result = self.login_client.service.login(self.username, self.password, )
            print(result)
            try:
                self.sessionID = result["sessionID"]
                with open(self.SESSION_FILE, 'wt') as file:
                    file.write(self.sessionID)

                return self.sessionID

            except AttributeError as e:
                raise LoginError('Login failed.')

    def logout(self):
        result = self.login_client.service.logout(self.sessionID)
        return result


    def create_type(self, type_name):
        ''' Provides short hand functions in creating Complex Types

            Usage:
                # Create the object with login creds.
                bp = webservices.BenefitPoint(username='you@me.net', password='password')

                # Create the type to pass into the search
                accountsearch = bp.create_type('ns1:AccountSearchCriteria')
                accountsearch.active = True

            Returns:
                Complex Type

        '''
        self.verify_login()

        token = self.client.factory.create('SessionIdHeader')
        token.sessionId = self.sessionID
        self.client.set_options(soapheaders=token)

        return self.client.factory.create(type_name)

    def list_methods(self):
        url = self.BROKER_CONNECTV4
        client = suds.client.Client(url)
        for service in client.wsdl.services:
            for port in service.ports:
                methods = port.methods.values()
                for method in methods:
                    print(method.name)
                    for part in method.soap.input.body.parts:
                        part_type = part.type
                        if (not part_type):
                            part_type = part.element[0]
                        print('  ' + str(part.name) + ': ' + str(part_type))
                        o = client.factory.create(part_type)
                        print('    ' + str(o))

    def get_client(self):
        self.verify_login()

        return self.client

    def get_current_user(self):
        self.verify_login()

        token = self.client.factory.create('SessionIdHeader')
        token.sessionId = self.sessionID
        self.client.set_options(soapheaders=token)
        user = self.login_client.service.getCurrentUser(self.sessionID)
        return (user)

    def get_activity_log_subjects(self):
        self.verify_login()

        token = self.client.factory.create('SessionIdHeader')
        token.sessionId = self.sessionID
        self.client.set_options(soapheaders=token)
        resp = self.client.service.getActivityLogSubjects()
        return (resp)

    def create_activity_log_record(self, activitylog):
        self.verify_login()

        token = self.client.factory.create('SessionIdHeader')
        token.sessionId = self.sessionID
        self.client.set_options(soapheaders=token)
        resp = self.client.service.createActivityLogRecord(activitylog)

        return (resp)

    def call(self, func, *args):
        ''' Pass in the method name and the search type object
            to call the method.

            Usage:
                from webservices import BenefitPoint
                bp = webservices.BenefitPoint(username='you@me.net', password='password')
                resp = bp.call('getTeamMembers', 1346911)

            Returns:
                results from method call

        '''
        self.verify_login()

        token = self.client.factory.create('SessionIdHeader')
        token.sessionId = self.sessionID
        self.client.set_options(soapheaders=token)
        try:
            if len(args):
                resp = getattr(self.client.service, func)(args, )
            else:
                resp = getattr(self.client.service, func)

        except suds.WebFault as detail:
            return "ERROR", detail

        return resp


if __name__ == "__main__":
    pass