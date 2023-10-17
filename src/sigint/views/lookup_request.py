"""
"""
import logging
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

from sigint.views.paganation import PaginationMixin
from sigint.models import LookupRequest, AddressResult
from sigint.serializers import LookupRequestSerializer, AddressResultSerializer

RESPONSE_DATE = timezone.datetime(1969,6,9,16,20,00).isoformat()
# LR_RESPONSE = openapi.Response('Lookup Request', LookupRequestSerializer)

RESPONSE_SCHEMAS = {
    "201": openapi.Response(
        description="201 Created",
        examples={
            "application/json": {
                "time": RESPONSE_DATE,
                "lookup_request": "<UUID>", 
                "status": "<queued>"
            }
        }
    ),
    "400": openapi.Response(
        description="400 Lookup Error",
        examples={
            "application/json": {
                "message": "There was a loss in cabin pressure on lookup 🔥",
                "time": RESPONSE_DATE,
                "lookup_request": "<UUID>", 
                "status": "<queued>"
            }
        }
    ),
}


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

    @swagger_auto_schema(
        tags=["Lookup Request"],
        responses=RESPONSE_SCHEMAS
    )
    def post(self, request):
        """
        Lookup Request Sync Create EP
        """
        from sigint.helpers.geo_lookup import GeoCheck
        from sigint.tasks import run_geo_lookup
        request_uuid = uuid.uuid4()
        lookup_request:LookupRequest = LookupRequest(
            uuid=request_uuid,
            user=request.user,
        )
        lookup_request.save()

        data = JSONParser().parse(request)
        lookups = data.get("lookups")
        run_type = data.get("type", "sync").lower()

        if run_type in ["async", "background", "job"]:
            run_geo_lookup.delay(
                request_uuid,
                lookups,
            )
            return Response(
                {"time": timezone.now(), "lookup_request": str(request_uuid), "status": lookup_request.status},
                status=status.HTTP_201_CREATED
            )
        elif run_type in ["sync", "keepalive", "wait"]:
            checker = GeoCheck(lookup_request=lookup_request)
            checker.run(requested=lookups)

            serializer = self.serializer_class(lookup_request)
            if lookup_request.status == "error":
                 return Response(
                    {"message": "There was a loss in cabin pressure on lookup 🔥", "time": timezone.now(), "lookup_request": str(request_uuid), "status": lookup_request.status},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(serializer.data)


class Results(APIView, PaginationMixin):
    """
    Lookup Request Detail View
    """
    queryset = AddressResult.objects.all()
    serializer_class = AddressResultSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_results(self, request_uuid):
        """
        Fetch Lookup Request Object
        """
        try:
            request = LookupRequest.objects.get(uuid=request_uuid)
            return AddressResult.objects.filter(lookup=request)
        except LookupRequest.DoesNotExist:
            raise Http404 from LookupRequest.DoesNotExist

    @swagger_auto_schema(tags=["Lookup Request"])
    def get(self, request, request_uuid):
        """
        Lookup Request Detail View
        """
        results = self.get_results(request_uuid)
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)
        


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
            return LookupRequest.objects.get(uuid=request_uuid)
        except LookupRequest.DoesNotExist:
            raise Http404 from LookupRequest.DoesNotExist

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
