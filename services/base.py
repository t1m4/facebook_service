from django.conf import settings
from facebook_business import FacebookSession
from facebook_business.adobjects.abstractcrudobject import AbstractCrudObject
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from rest_framework import serializers

from utils.utils import execute_error_message


class BaseFacebookService(object):
    def __init__(self, *args, **kwargs):
        self.FACEBOOK_ACCOUNT = kwargs.get('facebook_account')
        self.FACEBOOK_ACCESS_TOKEN = kwargs.get('access_token')
        self.APP_SECRET = kwargs.get('app_secret')
        self.APP_ID = kwargs.get('app_id')

        self.session = FacebookSession(self.APP_ID, self.APP_SECRET, self.FACEBOOK_ACCESS_TOKEN)
        self.api = FacebookAdsApi(self.session)

        self.account = AdAccount(self.FACEBOOK_ACCOUNT, api=self.api)
        self.initial_kwargs = kwargs

    def adobjects_factory_method(self, factory_class, *args, **kwargs) -> AbstractCrudObject:
        """
        Creating adobjects object with custom self.api as parameter to avoid using default self._api from library.
        """
        return factory_class(api=self.api, *args, **kwargs)

    @staticmethod
    def get_account(account_id=None):
        if not account_id:
            raise ValueError("Account_id is required parameter.")
        return AdAccount(account_id)

    def custom_request(self, params, endpoint, method=None, headers=None, files=None, is_json=True):
        if not method:
            method = FacebookAdsApi.HTTP_METHOD_GET
        response = self.api.call(
            method,
            "/".join((self.session.GRAPH, settings.API_VERSION, endpoint)),
            params=params,
            headers=headers,
            files=files,
        )
        if is_json:
            response = response.json()
        return response

    @staticmethod
    def get_graph_url():
        return FacebookSession.GRAPH

    def __exit__(self, exc_type, exc_value, traceback):
        self.api.close()
        self.session.close()

    @classmethod
    def initialize_service(cls, data):
        return cls(
            FACEBOOK_ACCOUNT=data.get('account_id'),
            access_token=data.get('access_token'),
            app_secret=data.get('app_secret') or settings.APP_SECRET,
            app_id=data.get('app_id') or settings.APP_ID,
        )

    def execute(self, func, attrs=None, not_raise_exception=None):
        if not attrs:
            attrs = {}
        try:
            return func(**attrs)
        except FacebookRequestError as e:
            self._handle_credentials_expiration(e)
            message = execute_error_message(e)
            if not not_raise_exception:
                raise serializers.ValidationError(message)
            else:
                return e

    def _handle_credentials_expiration(self, e):
        from account import constants, models

        api_error_code = e.api_error_code()
        api_error_subcode = e.api_error_subcode()
        if api_error_code == constants.EXPIRED_STATUS and api_error_subcode in constants.EXPIRED_SUB_STATUSES:
            credentials = models.FacebookExternalData.objects.filter(access_token=self.FACEBOOK_ACCESS_TOKEN).first()
            if not credentials:
                return
            credentials.is_expired = True
            credentials.save()
            raise serializers.ValidationError(
                {
                    "general": """Your access token is expired. Please update your integration settings.""",
                    "credentials_id": credentials.id,
                    "status": api_error_code,
                }
            )
