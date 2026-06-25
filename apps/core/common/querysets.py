# /opt/balthub/apps/core/common/querysets.py

from django.db import models


class PublicQuerySet(models.QuerySet):

    def public(self):
        return self.filter(
            is_deleted=False,
            is_public=True,
        )