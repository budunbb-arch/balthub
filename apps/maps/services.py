from apps.maps.models import MapSettings


class MapService:

    @classmethod
    def settings(cls):
        return MapSettings.get_solo()

    @classmethod
    def provider(cls):
        return cls.settings().provider

    @classmethod
    def api_key(cls):
        return cls.settings().api_key

    @classmethod
    def language(cls):
        return cls.settings().language

    @classmethod
    def js_url(cls):
        settings = cls.settings()

        if settings.provider == MapSettings.PROVIDER_YANDEX:
            return (
                "https://api-maps.yandex.ru/v3/"
                f"?apikey={settings.api_key}"
                f"&lang={settings.language}"
            )

        return None