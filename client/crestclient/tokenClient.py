#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crestclient\tokenClient.py
from crestClient import CrestUserBase
import requests
import requests.auth

class CrestUserSso(CrestUserBase):

    def __init__(self, token, server, verify = False, language = 'EN'):
        super(CrestUserSso, self).__init__(language)
        self.session = requests.session()
        self.server = server
        self.session.verify = verify
        self.session.keep_alive = False
        self.session.auth = CrestRefreshAuth(token)


class CrestRefreshAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.authorization = 'Bearer ' + token

    def __call__(self, request):
        if self.authorization:
            request.headers['Authorization'] = self.authorization
        request.register_hook('response', self.handle_response)
        return request

    def handle_response(self, response, **kwargs):
        if response.status_code == requests.codes.unauthorized:
            response.content
            response.raw.release_conn()
            response.request.headers['Authorization'] = self.get_authorization()
            new_response = response.connection.send(response.request, **kwargs)
            new_response.history.append(response)
            return new_response
        return response

    def get_authorization(self):
        return self.authorization
