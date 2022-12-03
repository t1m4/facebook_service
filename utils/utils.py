def ger_error(body):
    if body.get('error') and body.get('error').get('error_user_msg'):
        return body.get('error').get('error_user_msg')
    elif body.get('error') and body.get('error').get('error_user_title'):
        return body.get('error').get('error_user_title')
    elif body.get('error') and body.get('error').get('message'):
        return body.get('error').get('message')


def execute_error_message(e, default_message=None):
    if hasattr(e, 'body'):
        body = e.body()
        if isinstance(body, dict):
            return ger_error(body)
        elif isinstance(body, str):
            return body
    return default_message or 'FB api error. Try again or contact with administrator.'
