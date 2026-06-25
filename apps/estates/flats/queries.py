from apps.core.common.querysets import PublicQuerySet
from django.db.models import Min


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