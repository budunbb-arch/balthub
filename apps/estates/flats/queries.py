from apps.core.common.querysets import PublicQuerySet
from django.db.models import Min, Max


class FlatQuerySet(PublicQuerySet):

    def active(self):
        return self.public().filter(

            house__is_deleted=False,
            house__is_public=True,

            house__project__is_deleted=False,
            house__project__is_public=True,

            house__project__developer__is_deleted=False,
            house__project__developer__is_public=True,
        )

    def rooms(self, rooms):

        if not rooms:
            return self

        return self.filter(
            params__rooms__in=rooms
        )

    def square_from(self, value):

        if not value:
            return self

        return self.filter(
            params__square__gte=value
        )

    def square_to(self, value):

        if not value:
            return self

        return self.filter(
            params__square__lte=value
        )

    def min_price(self):

        return self.annotate(
            price=Min("deals__price")
        )

    def price_from(self, value):

        if not value:
            return self

        return self.filter(
            price__gte=value
        )

    def price_to(self, value):

        if not value:
            return self

        return self.filter(
            price__lte=value
        )

    def for_house(self, house):

        if not house:
            return self

        return self.filter(
            house=house
        )

    def room(self, room):

        if room is None:
            return self

        return self.filter(
            params__rooms=room
        )

    def sorted(self, value):

        allowed = {

            "rooms": "params__rooms",
            "-rooms": "-params__rooms",

            "square": "params__square",
            "-square": "-params__square",

            "price": "price",
            "-price": "-price",
        }

        return self.order_by(
            allowed.get(value, "price"),
            "id"
        )


    def price_limits(self):
        return self.aggregate(
            min_price=Min("deals__price"),
            max_price=Max("deals__price"),
        )
    

    def square_limits(self):

        return self.aggregate(
            min_square=Min("params__square"),
            max_square=Max("params__square"),
        )
    

    def available_rooms(self):

        return (
            self
            .exclude(params__rooms__isnull=True)
            .values_list(
                "params__rooms",
                flat=True,
            )
            .distinct()
            .order_by("params__rooms")
        )

    def floor_limits(self):

        return self.aggregate(
            min_floor=Min("params__floor"),
            max_floor=Max("params__floor"),
        )

    def ceiling_height_limits(self):

        return (
            self
            .exclude(params__ceiling_height=0)
            .aggregate(
                min_ceiling_height=Min("params__ceiling_height"),
                max_ceiling_height=Max("params__ceiling_height"),
            )
        )

    def square_limits(self):

        return self.aggregate(
            min_square=Min("params__square"),
            max_square=Max("params__square"),
        )

    def living_square_limits(self):

        return self.aggregate(
            min_living_square=Min("params__living_square"),
            max_living_square=Max("params__living_square"),
        )

    def kitchen_square_limits(self):

        return self.aggregate(
            min_kitchen_square=Min("params__kitchen_square"),
            max_kitchen_square=Max("params__kitchen_square"),
        )

    def floor_from(self, value):

        if not value:
            return self

        return self.filter(
            params__floor__gte=value
        )

    def floor_to(self, value):

        if not value:
            return self

        return self.filter(
            params__floor__lte=value
        )

    def ceiling_height_from(self, value):

        if not value:
            return self

        return self.filter(
            params__ceiling_height__gte=value
        ).exclude(params__ceiling_height=0)

    def ceiling_height_to(self, value):

        if not value:
            return self

        return self.filter(
            params__ceiling_height__lte=value
        ).exclude(params__ceiling_height=0)

    def living_square_from(self, value):

        if not value:
            return self

        return self.filter(
            params__living_square__gte=value
        )

    def living_square_to(self, value):

        if not value:
            return self

        return self.filter(
            params__living_square__lte=value
        )

    def kitchen_square_from(self, value):

        if not value:
            return self

        return self.filter(
            params__kitchen_square__gte=value
        )

    def kitchen_square_to(self, value):

        if not value:
            return self

        return self.filter(
            params__kitchen_square__lte=value
        )

    def rooms_alias(self, aliases):

        if not aliases:
            return self

        return self.filter(
            params__rooms_alias__in=aliases
        )

    def balcony_type(self, types):

        if not types:
            return self

        return self.filter(
            params__balcony_type__in=types
        )

    def bathroom_unit_type(self, types):

        if not types:
            return self

        return self.filter(
            params__bathroom_unit_type__in=types
        )

    def finish_type(self, types):

        if not types:
            return self

        return self.filter(
            params__finish_type__in=types
        )

    def haggle(self, value):

        if not value:
            return self

        return self.filter(
            deals__haggle=True
        ).distinct()

    def mortgage(self, value):

        if not value:
            return self

        return self.filter(
            deals__mortgage=True
        ).distinct()
