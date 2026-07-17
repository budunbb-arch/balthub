# /opt/balthub/apps/core/common/querysets.py

from django.db import models
from django.utils import timezone


class PublicQuerySet(models.QuerySet):

    def public(self):
        return self.filter(
            is_deleted=False,
            is_public=True,
        )

    def alive(self):
        return self.filter(
            is_deleted=False,
        )

    def soft_delete(self, user=None):
        values = {
            "is_deleted": True,
            "is_public": False,
            "deleted_at": timezone.now(),
        }

        if user:
            values["deleted_by"] = user

        return self.update(**values)