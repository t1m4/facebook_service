from django.conf import settings
from rest_framework import serializers

from account.models import FacebookExternalData
from account.selectors.integration import is_campaigns_exists
from account.services import exceptions
from services import account as account_service
from services import base
from utils.utils import execute_error_message


class IntegrationCreateUpdateService:
    def __init__(self, user) -> None:
        self._user = user

    def access_token_validate(self, validated_data):
        facebook_service = base.BaseFacebookService.initialize_service(validated_data)
        validate_token = facebook_service.custom_request(
            params={'access_token': facebook_service.FACEBOOK_ACCESS_TOKEN}, endpoint='me/'
        )
        if not isinstance(validate_token, dict):
            raise exceptions.InvalidAccessToken

    def _exchange_access_token(self, validated_data):
        try:
            facebook_service = base.BaseFacebookService.initialize_service(validated_data)
            exchange = facebook_service.custom_request(
                params={'access_token': facebook_service.FACEBOOK_ACCESS_TOKEN},
                endpoint='oauth/access_token?grant_type=fb_exchange_token'
                '&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={access_token}'.format(
                    app_id=facebook_service.APP_ID,
                    app_secret=facebook_service.APP_SECRET,
                    access_token=facebook_service.FACEBOOK_ACCESS_TOKEN,
                ),
            )
        except Exception as e:
            message = execute_error_message(e)
            raise serializers.ValidationError(message)

        return exchange

    def create_integration_data(self, validated_data):
        self.access_token_validate(validated_data)
        validated_data.pop("is_update_business_user_id", False)

        service = account_service.Account.initialize_service(validated_data)
        social_user_data = service.get_user_data(validated_data.get('account_id'))

        validated_data['business_user_id'] = social_user_data.get('business_user_id')
        validated_data['user_id'] = social_user_data.get('user_id')

        exchange = self._exchange_access_token(validated_data)

        validated_data['access_token'] = exchange.get('access_token')
        if not validated_data['access_token']:
            raise exceptions.EmptyAccessToken

        validated_data['company_id'] = self._user.profile.company_id
        validated_data['app_id'] = validated_data.get('app_id') or settings.APP_ID
        validated_data['app_secret'] = validated_data.get('app_secret') or settings.APP_SECRET

        account_data = service.get_account_data(validated_data.get('account_id'))
        validated_data["timezone_name"] = account_data.get("timezone_name")
        return validated_data

    def update_integration_data(self, instance: FacebookExternalData, validated_data):
        if (
            hasattr(instance, 'facebook_credentials')
            and is_campaigns_exists(instance)
            and validated_data["account_id"] != instance.account_id
        ):
            raise exceptions.InvalidAccoundId

        is_update_business_user_id = validated_data.pop("is_update_business_user_id", False)
        if (
            (instance.is_expired or instance.is_invalid_permissions)
            and validated_data.get("access_token")
            and validated_data["access_token"] != instance.access_token
        ):

            service_data = instance.service_data
            service_data["access_token"] = validated_data["access_token"]
            acs = account_service.Account.initialize_service(service_data)
            social_user_data = acs.get_user_data(instance.account_id)

            if str(instance.user_id) != str(social_user_data.get('user_id')):
                raise serializers.ValidationError(
                    "This integration was created with different account. Please, use same facebook account as ."
                )

            exchange = self._exchange_access_token(validated_data)

            if is_update_business_user_id:
                validated_data['business_user_id'] = social_user_data.get('business_user_id')

            validated_data['access_token'] = exchange.get('access_token')
            if not validated_data['access_token']:
                raise exceptions.EmptyAccessToken
                raise serializers.ValidationError({'access_token': "Something wrong with your access token."})
            validated_data["is_expired"] = False
        elif (
            not (instance.is_expired or instance.is_invalid_permissions)
            and validated_data.get("access_token")
            and validated_data["access_token"] != instance.access_token
        ):
            raise serializers.ValidationError({"access_token": "You can't change access_token when it's valid."})
        elif is_update_business_user_id:
            service_data = instance.service_data
            acs = account_service.Account.initialize_service(service_data)
            social_user_data = acs.get_user_data(instance.account_id)
            validated_data['business_user_id'] = social_user_data.get('business_user_id')

        if validated_data.get("is_update_timezone") or not instance.timezone_name:
            account_data = account_service.Account.initialize_service(validated_data).get_account_data(
                instance.account_id
            )
            validated_data["timezone_name"] = account_data.get("timezone_name")
