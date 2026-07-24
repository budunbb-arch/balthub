from apps.maps.services import MapService


def maps(request):
    return {
        "MAP_PROVIDER": MapService.provider(),
        "MAP_JS_URL": MapService.js_url(),
    }