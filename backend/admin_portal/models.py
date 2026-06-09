from django.db import models
from users.models import User


class AuditLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=200)
    target_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_entries'
    )
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'[{self.timestamp:%Y-%m-%d %H:%M}] {self.admin} — {self.action}'
