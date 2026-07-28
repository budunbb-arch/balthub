# /opt/balthub/apps/modules/ymaps.py

from apps.maps.engine import MapEngine


MODULE = "default/modules/ymaps.html"


def get_context(request, module):

    return {
        "points": MapEngine.all_houses(),
    }
