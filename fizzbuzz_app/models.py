from django.db import models

# Create your models here.

from django.db import models

class FizzBuzzRequest(models.Model):
    int1 = models.IntegerField()
    int2 = models.IntegerField()
    limit = models.IntegerField()
    str1 = models.CharField(max_length=255)
    str2 = models.CharField(max_length=255)
    hits = models.PositiveIntegerField(default=0)