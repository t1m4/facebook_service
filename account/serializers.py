import re

from django.conf import settings
from rest_framework import serializers

from account.services.integration import IntegrationCreateUpdateService
from services import account as account_service
from utils.rest_api.fields import LazyChoiceField, ListLazyChoiceField

from .models import FacebookExternalData


class BaseIntegrationSerializer(serializers.ModelSerializer):
    """
    Base class to work with integrations for Facebook.
    """

    using_in_campaigns = serializers.BooleanField(source='has_campaigns', read_only=True)


class FacebookIntegrationsSerializer(BaseIntegrationSerializer):
    access_token = serializers.CharField(required=True)
    account_id = LazyChoiceField(required=True, choices=account_service.get_user_ad_accounts)
    is_expired = serializers.BooleanField(read_only=True)
    is_update_timezone = serializers.BooleanField(default=False, write_only=False, required=False)
    is_update_business_user_id = serializers.BooleanField(default=False, write_only=True, required=False)
    page_source_businesses = ListLazyChoiceField(required=False, choices=account_service.get_all_businesses)

    class Meta:
        model = FacebookExternalData
        fields = (
            'id',
            'company_id',
            'account_id',
            'business_user_id',
            'user_id',
            'access_token',
            'status',
            'default',
            'name',
            'is_managed',
            'using_in_campaigns',
            "is_expired",
            'timezone_name',
            'integration_type',
            'is_invalid_permissions',
            'missed_permissions',
            'page_source_businesses',
            'is_update_business_user_id',
        )
        read_only_fields = (
            'id',
            'company_id',
            'status',
            'business_user_id',
            'user_id',
            "timezone_name",
            'is_invalid_permissions',
            'missed_permissions',
            'integration_type',
        )

    def validate(self, data):
        if self.instance:
            for field in ['access_token', 'app_id', 'app_secret']:
                if not data.get(field):
                    data[field] = getattr(self.instance, field)

        verify = account_service.Account.initialize_service(data).verify_credentials(
            data.get('app_id') or settings.APP_ID
        )
        if verify:
            raise serializers.ValidationError(verify)

        return super().validate(data)

    def validate_account_id(self, value):
        if not re.match(r'act_\d+', value):
            raise serializers.ValidationError({"account_id": "Account id should be in format 'act_12345'"})
        return value

    def create(self, validated_data):
        create_service = IntegrationCreateUpdateService(self.context['request'].user)
        created_data = create_service.create_integration_data(validated_data)
        instance = super().create(created_data)
        return instance

    def update(self, instance, validated_data):
        update_service = IntegrationCreateUpdateService(self.context['request'].user)
        updated_data = update_service.update_integration_data(instance, validated_data)
        instance = super().update(instance, updated_data)
        return instance


class FacebookManagedIntegrationSerializer(BaseIntegrationSerializer):
    class Meta:
        model = FacebookExternalData
        fields = (
            'id',
            'company_id',
            'account_id',
            'business_user_id',
            'user_id',
            'access_token',
            'status',
            'default',
            'name',
            'is_managed',
            'using_in_campaigns',
            "is_expired",
            'timezone_name',
            'is_invalid_permissions',
            'missed_permissions',
            'page_source_businesses',
            'is_update_business_user_id',
        )
        read_only_fields = (
            'user_id',
            'account_id',
            'access_token',
            'default',
            'business_user_id',
            'id',
            "timezone_name",
            'is_invalid_permissions',
            'missed_permissions',
        )
