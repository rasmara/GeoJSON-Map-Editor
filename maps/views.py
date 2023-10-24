from django.contrib.auth.decorators import login_required
from .models import GeoJSONPolygon, GeoJSONFeatures
from django.shortcuts import render, redirect
from .forms import GeoJSONImportForm
from django.http import JsonResponse
from django.shortcuts import render
from django.db import transaction
from django.conf import settings
from datetime import datetime
import json
import uuid


@login_required
@transaction.atomic  # To prevent partial data insertion in case of any errors
def import_geojson(request):
    if request.method == "POST":
        form = GeoJSONImportForm(request.POST)
        if form.is_valid():
            geojson_data = form.cleaned_data["geojson_data"]
            title = form.cleaned_data["title"]

            owner = request.user

            # updating properties with owner. first name & creation date
            new_properties = {
                "owner": owner.first_name,
                "email": owner.email,
                "creation date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            obj_polygon = GeoJSONPolygon(owner=owner, title=title)
            obj_polygon.save()

            features_lst = [
                GeoJSONFeatures(
                    features={
                        **feature,
                        "properties": {
                            **feature.get("properties", {}),
                            **new_properties,
                        },
                    },
                    geojson_data=obj_polygon,
                )
                for feature in geojson_data["features"]
            ]

            GeoJSONFeatures.objects.bulk_create(features_lst)

            return redirect("maps:map_display")

    else:
        form = GeoJSONImportForm()
    return render(request, "maps/import_geojson.html", {"form": form})


@login_required
def map_display(request):
    geojson_polygons = GeoJSONPolygon.objects.all()
    api_key = settings.GOOGLE_MAPS_API_KEY
    return render(
        request,
        "maps/map_display.html",
        {"api_key": api_key},
    )


@login_required
def load_geojson(request):
    """
    Once GeoJSON data is validated and stored; data for corresponding user will be
    retrieved from this API as an AJAX call.
    """
    user = request.user

    try:
        obj_geojson_features = GeoJSONFeatures.objects.filter(geojson_data__owner=user)

        features = [
            {
                **obj.features,
                "properties": {
                    **obj.features.get(
                        "properties", {}
                    ),  # Extend existing properties for infoWindow in map
                    "uuid": str(obj.uuid),
                    "infoTitle": obj.geojson_data.title,
                },
            }
            for obj in obj_geojson_features
        ]

        response_data = {"type": "FeatureCollection", "features": features}

        return JsonResponse(response_data, safe=False)

    except GeoJSONFeatures.DoesNotExist:
        # Handle the case where no features are found for the user
        return JsonResponse({"message": "No GeoJSON features found for this user."})

    except Exception as e:
        # Handle other exceptions, e.g., database errors
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def update_properties(request):
    """
    To update the properties for a specific existing polygon; AJAX request from user.
    """
    if request.method == "POST":
        try:
            post_data = json.loads(request.body)
            if validate_data(post_data):
                uuid_str = post_data["id"]
                properties = post_data["updated_data"]
                obj_geojson_features = GeoJSONFeatures.objects.filter(
                    uuid=uuid_str
                ).first()

                if not obj_geojson_features:
                    return JsonResponse({"error": "Polygon not found"})

                obj_geojson_features.features["properties"] = properties
                obj_geojson_features.save()

                properties.update(
                    {
                        "uuid": str(obj_geojson_features.uuid),
                        "infoTitle": obj_geojson_features.geojson_data.title,
                    }
                )

                return JsonResponse(
                    {
                        "message": "Properties updated successfully",
                        "properties": properties,
                    }
                )
            else:
                return JsonResponse({"error": "Invalid data"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"})
    else:
        return JsonResponse({"error": "Invalid request"})


def validate_data(data):
    """
    Custom validation for updating properties.
    """

    def has_keys(keys, data):
        return all(key in data for key in keys)

    if not has_keys(["id", "updated_data"], data):
        return False

    try:
        uuid.UUID(data["id"])
    except ValueError:
        return False

    if not isinstance(data["updated_data"], dict):
        return False

    # Implement additional validation checks for 'updated_data' here

    return True
