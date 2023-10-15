"""
"""
import uuid


from django.http import Http404
from django.utils import timezone

from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from skynet.views.paganation import PaginationMixin
from skynet.models import LookupRequest, AccessPlan
from skynet.serializers import LookupRequestSerializer


class List(APIView, PaginationMixin):
    """
    List/Create GeoSync View
    """
    queryset = LookupRequest.objects.all()
    serializer_class = LookupRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    @swagger_auto_schema(tags=["Lookup Request"])
    def get(self, request):
        """
        Lookup Request List EP
        """
        # pylint: disable=unused-argument
        owned = self.queryset.filter(user=request.user)

        page = self.paginate_queryset(owned)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

class Create(APIView, PaginationMixin):
    """
    List/Create GeoSync View
    """
    queryset = LookupRequest.objects.all()
    serializer_class = LookupRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    @swagger_auto_schema(
        tags=["Lookup Request"],
    )
    def post(self, request):
        """
        Lookup Request Sync Create EP
        """
        from skynet.helpers.geo_lookup import GeoCheck
        from skynet.helpers.quota_check import get_user_quota
        quota = get_user_quota(request.user)

        limit = None
        if quota["available"]["month"]:
            limit = quota["available"]["month"]

        if quota["available"]["day"]:
            limit = quota["available"]["day"]

        request_uuid = uuid.uuid4()
        lookup_request = LookupRequest(
            uuid=request_uuid,
            user=request.user,
        )
        lookup_request.save()

        data = JSONParser().parse(request)
        lookups = data.get("lookups")

        if limit:
            if lookups > limit:
                lookup_request.response_type = "quota"
                lookup_request.invalid_lookups = lookups
                lookup_request.save()
                serlized = self.serializer_class(lookup_request)
                data = {
                    "error": "Not enough quota",
                    "requested": len(lookups),
                    "quota": limit,
                    "lookup_request": serlized.data
                }
                return Response(data, status=status.HTTP_428_PRECONDITION_REQUIRED)


        checker = GeoCheck(lookup_request=lookup_request)
        checker.run(requested=lookups)

        serializer = self.serializer_class(data=lookup_request)
        return Response(serializer.data)


    @swagger_auto_schema(
        tags=["Lookup Request"],
    )
    def put(self, request):
        """
        GeoSync Create EP
        """
        from skynet.tasks import run_geo_lookup
        from skynet.helpers.quota_check import get_user_quota
        quota = get_user_quota(request.user)

        limit = None
        if quota["available"]["month"]:
            limit = quota["available"]["month"]

        if quota["available"]["day"]:
            limit = quota["available"]["day"]

        request_uuid = uuid.uuid4()
        lookup_request = LookupRequest(
            uuid=request_uuid,
            user=request.user,
        )
        lookup_request.save()

        data = JSONParser().parse(request)
        lookups = data.get("lookups")

        if limit:
            if lookups > limit:
                lookup_request.response_type = "quota"
                lookup_request.invalid_lookups = lookups
                lookup_request.save()
                serlized = self.serializer_class(lookup_request)
                data = {
                    "error": "Not enough quota",
                    "requested": len(lookups),
                    "quota": limit,
                    "lookup_request": serlized.data
                }
                return Response(data, status=status.HTTP_428_PRECONDITION_REQUIRED)

        run_geo_lookup.delay(
            request_uuid,
            lookups,
        )

        return Response(
            {"time": timezone.now(), "lookup_request": str(request_uuid), "status": "queued"},
            status=status.HTTP_201_CREATED
        )


class Detail(APIView, PaginationMixin):
    """
    Lookup Request Detail View
    """
    queryset = LookupRequest.objects.all()
    serializer_class = LookupRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_object(self, request_uuid):
        """
        Fetch Lookup Request Object
        """
        try:
            return LookupRequest.objects.get(UUID=request_uuid)
        except LookupRequest.DoesNotExist:
            raise Http404 from GeoSync.DoesNotExist

    @swagger_auto_schema(tags=["Lookup Request"])
    def get(self, request, request_uuid):
        """
        Lookup Request Detail View
        """
        lookup_request = self.get_object(request_uuid)
        serializer = self.serializer_class(lookup_request)
        return Response(serializer.data)

    @swagger_auto_schema(tags=["Lookup Request"])
    def delete(self, request, request_uuid):
        """
        Lookup Request Delete EP
        """
        lookup_request = self.get_object(request_uuid)
        lookup_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
