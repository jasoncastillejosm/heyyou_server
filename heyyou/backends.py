from core.models import User, Token


class TokenBackend(object):
    """Token authentication for API"""

    def authenticate(self, token=None):
        try:
            token = Token.objects.get(key=token)
            return token.user
        except Token.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
