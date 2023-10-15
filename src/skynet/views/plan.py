"""
"""
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from skynet.views.paganation import PaginationMixin
from skynet.models import  AccessPlan

class Quota(APIView, PaginationMixin):
    """
    Lookup Request Detail View
    """
    queryset = AccessPlan.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS


    @swagger_auto_schema(tags=["User Quota"])
    def get(self, request, request_uuid):
        """
        User Quota View
        """
        from skynet.helpers.quota_check import get_user_quota
        quota = get_user_quota(request.user)

        return Response(quota)
