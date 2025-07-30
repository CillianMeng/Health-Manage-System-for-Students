from django.db import models

# Create your models here.
class User(models.Model):
    userName = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=64)
    
    def __str__(self):
        return self.userName