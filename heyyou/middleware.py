from django.contrib.auth import authenticate


def get_token(request):
    """Get token from HTTP header"""

    if 'HTTP_AUTHORIZATION' in request.META:
        full_auth = request.META['HTTP_AUTHORIZATION'].split(' ')
        if len(full_auth) < 2 or full_auth[0] != 'Token':
            return None

        return full_auth[1].strip('"')
    return None


class AuthAPI(object):
    """
    Add user to request var for API calls
    Header format (RFC2617):
    Authorization: Token token="abcd1234"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # if request.get_full_path()[:4] != '/api':
        #     return self.get_response(request)

        token = get_token(request)
        if token:
            user = authenticate(token=token)
            if user and user.is_active:
                user.backend = 'core.backends.TokenBackend'
                request.user = user

        return self.get_response(request)
