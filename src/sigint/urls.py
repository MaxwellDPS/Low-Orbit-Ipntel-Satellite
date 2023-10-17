from django.urls import path
from sigint.views import (
   lookup_request,
   geo_sync
)

urlpatterns = [
    path('lookup/', lookup_request.List.as_view()),
    path('lookup/list', lookup_request.List.as_view()),
    path('lookup/<uuid:request_uuid>/', lookup_request.Detail.as_view()),
    path('lookup/<uuid:request_uuid>/results', lookup_request.Results.as_view()),
    path('lookup/create', lookup_request.Create.as_view()),

    path('geo/sync', geo_sync.CoolView.as_view()),
    path('geo/sync/<uuid:request_uuid>', geo_sync.SingleView.as_view()),
]
