class HouseMapModule:

    template = "default/modules/w_ymap.html"

    def get_context(self, request, house=None, **kwargs):

        if house is None:
            return {"enabled": False}

        params = getattr(house, "params", None)

        if not params:
            return {"enabled": False}

        if not params.latitude or not params.longitude:
            return {"enabled": False}

        return {
            "enabled": True,
            "latitude": params.latitude,
            "longitude": params.longitude,
        }