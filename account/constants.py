ACTIVE = 'active'
AUTHORIZING_ERROR = 'authorizing_error'
TOO_MANY_REQUESTS = 'too_many_requests'
PENDING = 'pending'

STATUSES = (
    (ACTIVE, 'Active'),
    (AUTHORIZING_ERROR, 'Authorizing error'),
    (TOO_MANY_REQUESTS, 'Too many requests'),
    (PENDING, 'SETUP PENDING'),
)

EXPIRED_STATUS = 190
EXPIRED_SUB_STATUSES = [460, 463, 464, 467, 492]
