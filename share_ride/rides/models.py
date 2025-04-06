from django.db import models
from utils.model_abstract import Model
from accounts.models import Profile

# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted=False)

RIDE_STATUSES = (
    ("requested", "Requested"),
    ("accepted", "Accepted"),
    ("started", "Started"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
)


class Ride(Model):
    rider = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ride_request')
    driver = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_rides')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=RIDE_STATUSES, default='requested')
    current_location = models.CharField(max_length=255, null=True, blank=True)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"Ride {self.id} - {self.rider.full_name} to {self.dropoff_location}"