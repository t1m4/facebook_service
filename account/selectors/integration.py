def is_campaigns_exists(credential):
    return credential.facebook_credentials.all().exists()
    return False
