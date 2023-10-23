import uuid
from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


class GeoJSONPolygon(models.Model):
    title = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "GeoJSONPolygon"


class GeoJSONFeatures(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    features = models.JSONField(null=True)
    geojson_data = models.ForeignKey("GeoJSONPolygon", on_delete=models.CASCADE)

    class Meta:
        db_table = "GeoJSONFeatures"
