# apps/core/documents/models.py

from django.db import models


class Document(models.Model):

    document_name = models.CharField(max_length=255, verbose_name="Название документа")
    document_content = models.TextField(verbose_name="HTML содержимое")
    document_file = models.FileField(upload_to="documents/", blank=True, null=True, verbose_name="Файл документа")
    document_date = models.DateField(auto_now=True, null="True", verbose_name="Дата документа")
    document_public = models.BooleanField(default=False, verbose_name="Публичный")
    document_status = models.CharField(
        max_length=20,
        choices=[
            ("project", "Проект"),
            ("released", "Выпущен"),
        ],
        default="project",
        verbose_name="Статус",
    )
    document_comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ["-document_date", "-id"]

    def __str__(self):
        return self.document_name or str(self.id)