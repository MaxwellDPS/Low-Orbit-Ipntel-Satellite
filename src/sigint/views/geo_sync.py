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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from sigint.views.paganation import PaginationMixin
from sigint.models import GeoSync
from sigint.serializers import GeoSyncSerializer
from sigint.views.permissions import IsGeoAdminUser
from django_db_geventpool.utils import close_connection

RESPONSE_DATE = timezone.datetime(1969,6,9,16,20,00).isoformat()
GEO_RESPONSE = openapi.Response('GeoSync', GeoSyncSerializer).as_odict()
RESPONSE_SCHEMAS = {
#    "200": GeoSyncSerializer,
    "201": openapi.Response(
        description="201 Created",
        examples={
            "application/json": {
                "time": RESPONSE_DATE,
                "uuid": "<UUID>", 
                "status": "<queued>"
            }
        }
    ),
}

LIST_RESPONSE_SCHEMAS = {
    "200": openapi.Response(
        description="200 Success",
        examples={
            "application/json": {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    GeoSyncSerializer
                ]
            }
        }
    ),
}
    

class CoolView(APIView, PaginationMixin):
    """
    List/Create GeoSync View
    """
    queryset = GeoSync.objects.all()
    serializer_class = GeoSyncSerializer
    permission_classes = [IsGeoAdminUser]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
  

    @swagger_auto_schema(tags=["Geo Sync"], responses={200: GeoSyncSerializer(many=True)} )
    @close_connection
    def get(self, request):
        """
        Geo Sync List EP
        """
        # pylint: disable=unused-argument

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    
    @swagger_auto_schema(
        tags=["Geo Sync"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "force": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="Force a Sync even if not time"
                ),
            },
        responses=RESPONSE_SCHEMAS
        ),
    )
    @close_connection
    def post(self, request):
        """
        GeoSync Create EP
        """
        from sigint.tasks import sync_maxmind_database
        data = JSONParser().parse(request)


        force = data.get("force", False)
        sync_uuid = uuid.uuid4()
        sync_maxmind_database.delay(force=force, sync_uuid=sync_uuid)

        return Response(
            {"time": timezone.now(), "uuid": str(sync_uuid), "status": "queued"},
            status=status.HTTP_201_CREATED
        )


class SingleView(APIView, PaginationMixin):
    """
    Single GeoSync View
    """
    serializer_class = GeoSyncSerializer
    permission_classes = [IsGeoAdminUser]
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get_object(self, request_uuid):
        """
        Fetch GeoSync Object
        """
        try:
            return GeoSync.objects.get(uuid=request_uuid)
        except GeoSync.DoesNotExist:
            raise Http404 from GeoSync.DoesNotExist

    @swagger_auto_schema(tags=["Geo Sync"], operation_description="Get Geo Sync Object")
    @close_connection
    def get(self, request, request_uuid):
        """
        GeoSync Transmission list EP
        """
        geo_sync = self.get_object(request_uuid)
        serializer = self.serializer_class(geo_sync)
        return Response(serializer.data)

    @swagger_auto_schema(tags=["Geo Sync"])
    @close_connection
    def delete(self, request, request_uuid):
        """
        GeoSync Delete EP
        """

        geo_sync = self.get_object(request_uuid)
        geo_sync.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
