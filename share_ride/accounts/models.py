from django.db import models
from utils.model_abstract import Model
from django.contrib.auth.models import User

# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, deleted=False)


USER_TYPES = (
    ("rider", "Rider"),
    ("driver", "Driver"),
)


class Profile(Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=40, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=255, null=True)
    user_type = models.CharField(max_length=150, choices=USER_TYPES, null=True)
    is_active = models.BooleanField(default=True)
    current_latitude = models.FloatField(null=True, blank=True)  
    current_longitude = models.FloatField(null=True, blank=True) 
    objects = ActiveManager()

    def __str__(self):
        return self.first_name
    
    @property
    def full_name(self):
        return self.first_name + " " + self.last_name if self.last_name is not None else self.first_name