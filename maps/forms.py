import json
from django import forms
from .models import GeoJSONPolygon


# Form for importing geojson data; Title & data
class GeoJSONImportForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter a title"}
        ),
        label="Title",
    )

    geojson_data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 30,
                "class": "form-control",
                "placeholder": """Enter your GeoJSON data here \n
    {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            [
              16.689685322656658,
              10.628909271029912
            ],
            [
              22.254464559428243,
              -5.926519105208044
            ],            
          ]
        ],
        "type": "Polygon"
      }
    }""",
            }
        ),
        label="GeoJSON Data",
    )

    def clean_geojson_data(self):
        """

        Validating the GeoJSON data with respect to GeoJSON Format (RFC 7946)
        1. Data should be in JSON format
        2. Should have keys specific to GeoJSON( "type", "Features" , "Properties" etc)

        """
        geojson = self.cleaned_data["geojson_data"]

        try:
            json_data = json.loads(geojson)

            if "type" not in json_data or json_data["type"] != "FeatureCollection":
                raise forms.ValidationError(
                    "GeoJSON should contain 'type':'FeatureCollection' "
                )

            features = json_data.get("features")
            if features:
                for feature in features:
                    if (
                        "geometry" not in feature
                        or "coordinates" not in feature["geometry"]
                    ):
                        raise forms.ValidationError(
                            "Feature in FeatureCollection does not contain 'geometry' or 'coordinates'"
                        )
            else:
                raise forms.ValidationError("GeoJSON should contain key 'features'")

        except (ValueError, TypeError):
            raise forms.ValidationError("Invalid JSON format")

        return json_data
