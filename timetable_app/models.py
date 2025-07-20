from django.db import models

# Create your models here.
from django.db import models


class Timetable(models.Model):
    CATEGORY_CHOICES = [
        ('junior-secondary', 'Junior Secondary'),
        ('upper-primary', 'Upper Primary'),
        ('lower-primary', 'Lower Primary'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    data = models.JSONField(default=dict)

    def __str__(self):
        return self.category