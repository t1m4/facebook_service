from rest_framework import serializers


class InvalidAccessToken(serializers.ValidationError):
    def __init__(self):
        super().__init__({'access_token': 'Invalid access_token or app_secret.'})


class EmptyAccessToken(serializers.ValidationError):
    def __init__(self):
        super().__init__({'access_token': "Something wrong with your access token."})


class InvalidAccoundId(serializers.ValidationError):
    def __init__(self):
        super().__init__({"account_id": "Ad account id can't be changed, because it's already used at campaign."})


class InvalidUserId(serializers.ValidationError):
    def __init__(self):
        super().__init__(
            "This integration was created with different account. Please, use same facebook account as integration."
        )


class ValidAccessToken(serializers.ValidationError):
    def __init__(self):
        super().__init__({"access_token": "You can't change access_token when it's valid."})
