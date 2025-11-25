from django.urls import path
from . import views

app_name = "agua"

urlpatterns = [
    #path("", views.inicio, name="inicio"),
    path("", views.resumen_propiedades, name="resumen"),
    path("bw/", views.correlacion_bw, name="correlacion_bw"),
    path("rsw/", views.correlacion_rsw, name="correlacion_rsw"),
    path("viscosidad/", views.correlacion_viscosidad, name="correlacion_viscosidad"),
    path("compresibilidad/", views.correlacion_compresibilidad, name="correlacion_compresibilidad"),
    path("densidad/", views.correlacion_densidad, name="correlacion_densidad"),
]