
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.utils import datetime_from_epoch

from .models import BlacklistedAccessToken, OutstandingAccessToken


class CustomAccessToken(AccessToken):

    @classmethod
    def for_user(cls, user):
        """
        Overrides the default for_user method to store the access token in the OutstandingAccessToken model.
        """
        access_token = super().for_user(user)
        while True:
            if not cls.is_token_present(access_token):
                break
            access_token = super().for_user(user)
        access_token.create_outstanding_access_tokens()
        return access_token
    
    @classmethod
    def is_token_present(cls, access_token):
        """
        Checks if the access token is present in either the outstanding or blacklisted access tokens.
        """
        access_token_str = str(access_token)
        if OutstandingAccessToken.objects.filter(token=access_token_str).exists():
            outstanding_token = OutstandingAccessToken.objects.get(token=access_token_str)
            if BlacklistedAccessToken.objects.filter(token=outstanding_token).exists():
                return True
        return False
    
    def blacklist_on_logout(self):
        jti = self.payload[settings.SIMPLE_JWT.get("JTI_CLAIM", "jti")]
        exp = self.payload["exp"]

        token, _ = OutstandingAccessToken.objects.get_or_create(
            jti=jti,
            defaults={
                "token": str(self),
                "expires_at": datetime_from_epoch(exp),
            },
        )

        return BlacklistedAccessToken.objects.get_or_create(token=token)

    def create_outstanding_access_tokens(self):
        access_token = str(self)
        user_id = self.get("user_id", None)

        jti = self[settings.SIMPLE_JWT.get("JTI_CLAIM", "jti")]
        exp = self["exp"]

        access_token_obj = OutstandingAccessToken.objects.create(
                user_id=user_id,
                jti=jti,
                token=str(access_token),
                created_at=self.current_time,
                expires_at=datetime_from_epoch(exp),
        )
        return access_token_obj

    def remove_from_outstanding_tokens(self):
        access_token = str(self)
        OutstandingAccessToken.objects.filter(token=access_token).delete()

    def check_blacklist(self):
        jti = self.payload[settings.SIMPLE_JWT.get("JTI_CLAIM", "jti")]
        if BlacklistedAccessToken.objects.filter(token__jti=jti).exists():
            raise InvalidToken("Token is blacklisted")


class CustomRefreshToken(RefreshToken):
    access_token_class = CustomAccessToken

    @classmethod
    def for_user(cls, user):
        """
        Overrides the default for_user method to add the token to the outstanding token list.
        """
        refresh_token = super().for_user(user)
        access_token = refresh_token.access_token_class.for_user(user)
        return refresh_token, access_token
    
    @classmethod
    def refresh_tokens(cls, user, old_refresh_token):
        """
        Refreshes tokens, blacklists the old refresh token, sets necessary claims, 
        and returns new access and refresh tokens.
        """

        old_refresh = cls(old_refresh_token)
        cls.blacklist_access_tokens_by_user(old_refresh.get("user_id", None))

        # Generate a new refresh token
        new_refresh_token, new_access_token = cls.for_user(user)

        if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
            if settings.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION", False):
                try:
                    old_refresh.blacklist()
                except AttributeError:
                    pass

        return new_refresh_token, new_access_token

    @classmethod
    def blacklist_access_tokens_by_user(cls, user_id):
        """
        Blacklists all access tokens associated with the provided user ID.
        """
        try:
            outstanding_tokens = OutstandingAccessToken.objects.filter(user_id=user_id)
            
            for token in outstanding_tokens:
                BlacklistedAccessToken.objects.get_or_create(token=token)

            return True
        except Exception:
            return False



class JWTAuthenticationWithBlackList(JWTAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        validated_token.check_blacklist()

        return self.get_user(validated_token), validated_token