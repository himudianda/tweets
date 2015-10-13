
class TweetException(Exception):
    def __init__(self, msg, resource_url=None, request_method=None, status_code=None, error_code=None, headers=None):
        self._msg = msg
        self.request_method = request_method
        self.resource_url = resource_url
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers

    def __str__(self):
        if self.request_method and self.resource_url:
            return '%s (%s %s)' % (self._msg, self.request_method, self.resource_url)
        return self._msg


class ApiError(TweetException):
    def __init__(self, msg, response=None, request_method=None, error_code=None):
        kwargs = {}
        if response is not None:
            kwargs = {
                'status_code': response.status_code,
                'resource_url': response.url,
                'headers': response.headers,
            }

        super(ApiError, self).__init__(
            msg,
            request_method=request_method,
            error_code=error_code,
            **kwargs
        )


class RateLimitError(ApiError):
    pass


class AuthError(ApiError):
    pass


class ClientError(TweetException):
    pass
