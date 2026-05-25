from django.db import models


class Configuration(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} = {self.value}"


class SiteVisit(models.Model):
    date = models.DateField()
    ip_hash = models.CharField(max_length=64)

    class Meta:
        unique_together = [("date", "ip_hash")]
