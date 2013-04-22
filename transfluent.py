import base64

import requests

TRANSFLUENT_URL = 'https://transfluent.com/v2/'


class Transfluent(object):
    def __init__(self, token=None):
        self.token = token
        self._transfluent_url = TRANSFLUENT_URL

    def _request(self, method, path, data=None):
        url = self._transfluent_url + path
        kwargs = {}
        if method.upper() == 'GET':
            kwargs['params'] = data
        elif method.upper() == 'POST':
            kwargs['data'] = data
        else:
            raise ValueError('Unsupported request method: {0}'.format(method))
        response = requests.request(method, url, **kwargs)
        if response.status_code != 200:
            raise TransfluentError(response)
        data = response.json()
        return data['response']

    def _authed_request(self, method, path, data=None):
        data = data or {}
        data['token'] = self.token
        return self._request(method, path, data)

    def authenticate(self, email, password):
        data = {'email': email, 'password': password}
        response = self._request('GET', 'authenticate', data)
        self.token = response['token']

    @property
    def customer_name(self):
        return self._authed_request('GET', 'customer/name')

    @customer_name.setter
    def customer_name(self, name):
        self._authed_request('POST', 'customer/name', {'name': name})

    @property
    def customer_email(self):
        return self._authed_request('GET', 'customer/email')

    @customer_email.setter
    def customer_email(self, email):
        self._authed_request('POST', 'customer/email', {'email': email})

    @property
    def languages(self):
        return self._request('GET', 'languages')

    def file_save(self, identifier, language, file, type, format='UTF-8',
                  save_only_data=False):
        try:
            content = file.read()
        except AttributeError:
            content = str(file)
        data = {
            'identifier': identifier,
            'language': language,
            'format': format,
            'content': base64.b64encode(content),
            'type': type,
            'save_only_data': int(save_only_data)
        }
        return self._authed_request('POST', 'file/save', data)

    def file_status(self, identifier, language):
        data = {
            'identifier': identifier,
            'language': language,
        }
        return self._authed_request('GET', 'file/status', data)


class TransfluentError(Exception):
    def __init__(self, response):
        data = response.json()
        self.response = response
        self.type = data['error']['type']
        self.message = data['error']['message']

    def __repr__(self):
        return '<TransfluentError [{0}]>'.format(self.type)

    def __str__(self):
        return self.message