from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_events',
    )
    method = models.CharField(max_length=8)
    path = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Evento de auditoría'
        verbose_name_plural = 'Eventos de auditoría'

    def __str__(self):
        return f'{self.method} {self.path} ({self.status_code})'
