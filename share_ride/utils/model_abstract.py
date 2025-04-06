from django.db import models


class SoftDeletionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At', help_text='Date and time the service was created')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At', help_text='Date and time the service was last updated')
    deleted = models.BooleanField(default=False)

    objects = SoftDeletionManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self):
        self.deleted = True
        self.save()
    
    def restore(self):
        self.deleted = False
        self.save()

    def hard_delete(self):
        super().delete()