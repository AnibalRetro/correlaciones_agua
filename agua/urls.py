from django.urls import path
from . import views

app_name = "agua"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("bw/", views.correlacion_bw, name="correlacion_bw"),
    path("rsw/", views.correlacion_rsw, name="correlacion_rsw"),
]
