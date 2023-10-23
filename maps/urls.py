from django.urls import path
from . import views

app_name = "maps"

urlpatterns = [
    path("import-geojson/", views.import_geojson, name="import_geojson"),
    path("view-map/", views.map_display, name="map_display"),
    path("load-geojson", views.load_geojson, name="load_geojson"),
    path("update-properties", views.update_properties, name="update_properties"),
]
