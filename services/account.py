from django.conf import settings
from facebook_business.exceptions import FacebookRequestError
from rest_framework import serializers

from utils.utils import execute_error_message

from .base import BaseFacebookService


def execute_access_token_from_request(context):
    request, view = context['request'], context['view']

    try:
        integration = view.get_object()
    except (AssertionError, AttributeError):
        integration = None

    access_token = request.GET.get('access_token') or request.data.get('access_token')
    if not access_token and integration:
        access_token = integration.access_token

    return access_token


def get_user_ad_accounts(context):
    if context["request"].method == 'GET':
        return []

    access_token = execute_access_token_from_request(context)

    if not access_token:
        raise serializers.ValidationError({'access_token': 'Required field'})

    facebook_service = BaseFacebookService(access_token=access_token)

    accounts = facebook_service.execute(
        facebook_service.custom_request,
        dict(params={'access_token': access_token, "limit": 5000}, endpoint='me/adaccounts?fields=name'),
    )
    return [(ad_account.get('id'), ad_account.get('name')) for ad_account in accounts.get('data', [])]


def get_all_businesses(context):
    if context["request"].method == 'GET':
        return []

    access_token = execute_access_token_from_request(context)

    if not access_token:
        raise serializers.ValidationError({'access_token': 'Required field'})

    account_id = context["request"].GET.get("account_id") or context["request"].data.get("account_id")

    if not account_id:
        return []

    service = Account.initialize_service(
        {
            "access_token": access_token,
            "account_id": account_id,
            "app_secret": settings.APP_SECRET,
            "app_id": settings.APP_ID,
        }
    )

    data = dict((item.get("id"), item.get("name")) for item in service.get_parent_business_id() if item)
    return data.items()


class Account(BaseFacebookService):
    def verify_credentials(self, app_id):
        invalid_token_response = {'access_token': 'Invalid access_token or app_secret.'}
        invalid_app_response = {'app_id': 'Invalid app_id.'}

        try:
            validate_token = self.execute(
                self.custom_request, dict(params={'access_token': self.FACEBOOK_ACCESS_TOKEN}, endpoint='me/')
            )
            if not isinstance(validate_token, dict):
                return invalid_token_response
        except FacebookRequestError as e:
            return execute_error_message(e)

        try:
            validate_app = self.execute(self.custom_request, dict(params={}, endpoint=str(app_id)))
            if not isinstance(validate_app, dict):
                return invalid_app_response
        except FacebookRequestError as e:
            return execute_error_message(e)

    def get_user_data(self, account_id):
        data = {}

        business_users = self.execute(
            self.custom_request,
            dict(
                params={},
                endpoint='me/business_users?fields=assigned_ad_accounts.limit(1000),business.limit(1000)&limit=1000',
            ),
        ).get("data", [])

        user_data = self.execute(self.custom_request, dict(params={}, endpoint='me'))
        data['user_id'] = user_data.get('id')

        for business_user in business_users:
            assigned_ad_accounts = business_user.get('assigned_ad_accounts', {}).get('data', [])
            for assigned_ad_account in assigned_ad_accounts:
                if assigned_ad_account.get('id') == account_id:
                    data['business_user_id'] = business_user.get('id')
                    break

            if 'business_user_id' in data:
                break
        return data

    def get_account_data(self, account_id):
        return self.execute(self.account.remote_read, {"fields": ["timezone_name"]})

    def get_parent_business_id(self):
        return self.execute(self.account.remote_read, {"fields": ["business"]}).get("business", {}).get("id")
