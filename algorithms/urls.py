from django.urls import include, path
from .views import *

app_name = "algorithms"
urlpatterns = [
    path("dynamic/", dynamic, name="dynamic"),
    path("boyer_moore/", boyer_moore, name="boyer_moore"),
    path("calc_dynamic/", calc_dynamic, name="calc_dynamic"),
    path("calc_boyer_moore/", calc_boyer_moore, name="calc_boyer_moore"),
]
