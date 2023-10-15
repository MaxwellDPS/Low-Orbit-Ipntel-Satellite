from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic.base import RedirectView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


SchemaView = get_schema_view(
   openapi.Info(
      title="Where TF API",
      default_version='v1',
      description="Find Dat IP™",
      #contact=openapi.Contact(email="mwatermolen@maxwelldps.com"),
      license=openapi.License(name="AGPLv3 License"),
   ),
   public=True,
   permission_classes=[permissions.IsAuthenticatedOrReadOnly],
)


urlpatterns = [
    re_path(r'^api/$', RedirectView.as_view(url='/api/v1', permanent=False)),
    re_path(r'api/v1/auth/', include('durin.urls')),
    re_path(r'^api/v1/$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/', include('skynet.urls')),
    path('admin/', admin.site.urls),
]
