# /opt/balthub/apps/modules/ymaps.py

from apps.maps.engine import MapEngine


MODULE = "default/modules/ymaps.html"


def get_context(request, module):

    points = MapEngine.all_houses() or []

    if module.position == "footer":
        points = [{
            "lon": 20.508214,
            "lat": 54.711364,
            "title": "",
        }]

    return {
        "points": points,
    }
