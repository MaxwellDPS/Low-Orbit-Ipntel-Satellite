"""
"""
"""
"""
from datetime import timedelta
from django.db.models import Sum, Q
from django.utils import timezone
from django.contrib.auth.models import User

from skynet.models import LookupRequest, AccessPlan


def get_user_quota(user: User):
    """
    Lookup Request Detail View
    """

    plans = AccessPlan.objects.filter(Q(users=user)|Q(groups__in=user.groups))

    allowed_lookups_per_day = plans.aggregate(Sum('allowed_lookups_per_day'))
    allowed_lookups_per_month = plans.aggregate(Sum('allowed_lookups_per_month'))

    user_lookups = LookupRequest.objects.filter(user=user)
    daily_lookups = user_lookups.filter(time__gte=timezone.now() - timedelta(days=1))
    monthly = user_lookups.filter(time__gte=timezone.now() - timedelta(days=30))
    daily_lookups_used = daily_lookups.aggregate(Sum('valid_lookups'))
    monthly_lookups_used = monthly.aggregate(Sum('valid_lookups'))

    response = {
        "total_quota": {
            "day": allowed_lookups_per_day if not allowed_lookups_per_day == 0 else "unlimited",
            "month": allowed_lookups_per_month if not allowed_lookups_per_month == 0 else "unlimited",
        },
        "used":{
            "day":{
                "used": daily_lookups_used,
                "rolling_check_time": (timezone.now() - timedelta(days=1)).isoformat()
            },
            "month":{
                "used": monthly_lookups_used,
                "rolling_check_time": (timezone.now() - timedelta(days=1)).isoformat()
            }
        },
        "available":{
            "day": allowed_lookups_per_day - daily_lookups_used if allowed_lookups_per_day == 0 else None,
            "month": allowed_lookups_per_month - monthly_lookups_used  if allowed_lookups_per_month == 0 else None
        },
    }

    return response
