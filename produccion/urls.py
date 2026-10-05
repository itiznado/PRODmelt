from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from calculo.api_views import RegistroViewSet

router = DefaultRouter()
router.register(r"registros", RegistroViewSet, basename="registro")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django.contrib.auth.urls")),
    path("", include("calculo.urls")),
    path("api/", include(router.urls)),
    path("api/token/", obtain_auth_token, name="api_token"),
]