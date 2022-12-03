from django.contrib.postgres.fields import ArrayField
from django.db import models

from . import constants
from .selectors.integration import is_campaigns_exists


class FacebookExternalData(models.Model):
    created_at = models.DateTimeField(null=True)
    is_managed = models.BooleanField(default=False)

    company_id = models.IntegerField(null=False, blank=False)

    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=constants.STATUSES, default=constants.ACTIVE)
    default = models.BooleanField(default=True)

    account_id = models.CharField(max_length=50, null=True)
    user_id = models.BigIntegerField(null=True)
    business_user_id = models.BigIntegerField(null=True)

    access_token = models.CharField(max_length=1250, null=True)
    app_secret = models.CharField(max_length=300, null=True)
    app_id = models.BigIntegerField(null=True)

    is_expired = models.BooleanField(default=False)
    is_invalid_permissions = models.BooleanField(default=False)

    missed_permissions = models.CharField(max_length=3000, null=True, blank=True)

    timezone_name = models.CharField(max_length=100, null=True, blank=True)

    page_source_businesses = ArrayField(models.CharField(max_length=250), default=list)

    @property
    def headers(self):
        return {'X-Access-Token': self.access_token, 'X-APP-Secret': self.app_secret, 'X-APP-Id': str(self.app_id)}

    @property
    def service_data(self):
        return {
            'access_token': self.access_token,
            'app_secret': self.app_secret,
            'app_id': self.app_id,
            'account_id': self.account_id,
        }

    def has_campaigns(self):
        return is_campaigns_exists(self)
