from streamer_exceptions import ApiError, RateLimitError, AuthError, ClientError
from requests_oauthlib import OAuth1Session
import requests
import json

__version__ = 1.0
TWITTER_API_VERSION = '1.1'
TWITTER_BASE_API_URL = 'https://%s.twitter.com'


class StreamResponse(object):
    def __init__(self, response, request_method):
        self.resource_url = response.url
        self.headers = response.headers
        self.request_method = request_method
        self._stream_iter = response.iter_lines

    def __repr__(self):
        return '<%s: %s %s>' % (self.__class__.__name__, self.request_method, self.resource_url)

    def stream(self):
        for item in self._stream_iter():
            if item:
                try:
                    data = json.loads(item)
                except:
                    pass
                else:
                    yield data


class ApiComponent(object):
    def __init__(self, client, path=None):
        self._client = client
        self._path = path

    def __repr__(self):
        return '<ApiComponent: %s>' % self._path

    def __getitem__(self, path):
        if self._path is not None:
            path = '%s/%s' % (self._path, path)
        return ApiComponent(self._client, path)

    def __getattr__(self, path):
        return self[path]

    def get(self, **params):
        if self._path is None:
            raise TypeError('Calling get() on an empty API path is not supported.')
        return self._client.request('GET', self._path, **params)

    def post(self, **params):
        if self._path is None:
            raise TypeError('Calling post() on an empty API path is not supported.')
        return self._client.request('POST', self._path, **params)


class StreamClient(object):
    api_version = TWITTER_API_VERSION
    base_api_url = TWITTER_BASE_API_URL
    user_agent_string = 'Birdy Twitter Client v%s' % __version__

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.session = self.get_oauth_session()

    def configure_oauth_session(self, session):
        session.headers = {'User-Agent': self.user_agent_string}
        return session

    def get_oauth_session(self):
        return self.configure_oauth_session(OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.access_token,
            resource_owner_secret=self.access_token_secret)
        )

    def __getattr__(self, path):
        return ApiComponent(self, path)

    def request(self, method, path, **params):
        method = method.upper()
        url = self.construct_resource_url(path)
        request_kwargs = {}
        params, files = self.sanitize_params(params)

        if method == 'GET':
            request_kwargs['params'] = params
        elif method == 'POST':
            request_kwargs['data'] = params
            request_kwargs['files'] = files

        try:
            response = self.make_api_call(method, url, **request_kwargs)
        except requests.RequestException as e:
            raise ClientError(
                str(e),
                resource_url=url,
                request_method=method
            )

        return self.handle_response(method, response)

    def construct_resource_url(self, path):
        paths = path.split('/')
        return '%s/%s/%s.json' % (self.base_api_url % paths[0], self.api_version, '/'.join(paths[1:]))

    @staticmethod
    def sanitize_params(input_params):
        params, files = ({}, {})

        for k, v in input_params.items():
            if hasattr(v, 'read') and callable(v.read):
                files[k] = v
            elif isinstance(v, bool):
                if v:
                    params[k] = 'true'
                else:
                    params[k] = 'false'
            elif isinstance(v, list):
                params[k] = ','.join(v)
            else:
                params[k] = v
        return params, files

    def make_api_call(self, method, url, **request_kwargs):
        return self.session.request(method, url, stream=True, **request_kwargs)

    def handle_response(self, method, response):

        if response.status_code == 200:
            return StreamResponse(response, method)

        kwargs = {
            'request_method': method,
            'response': response,
        }

        if response.status_code == 401:
            raise AuthError('Unauthorized.', **kwargs)

        if response.status_code == 404:
            raise ApiError('Invalid API resource.', **kwargs)

        if response.status_code == 420:
            raise RateLimitError(response.content, **kwargs)

        raise ApiError(response.content, **kwargs)
