from django.urls import path
from skynet.views import (
   lookup_request,
   geo_sync,
   plan
)

urlpatterns = [
    path('lookup/', lookup_request.List.as_view()),
    path('lookup/list', lookup_request.List.as_view()),
    path('lookup/<uuid:object_uuid>/', lookup_request.Detail.as_view()),
    path('lookup/create', lookup_request.Create.as_view()),

    path('geo/sync', geo_sync.CoolView.as_view()),
    path('geo/sync/<uuid:object_uuid>', geo_sync.SingleView.as_view()),

    path('plan/quota', plan.Quota.as_view()),

]
