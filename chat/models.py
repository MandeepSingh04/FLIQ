from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from autoslug import AutoSlugField

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return str(self.name)

class Message(models.Model):
    value = models.CharField(max_length=1000000)
    date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=1000000)
    name = models.CharField(max_length=30)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    slug = AutoSlugField(populate_from='user')
    room = models.CharField(max_length=10000000)
    read = models.CharField(max_length=1000000)

    def mark_as_read(self):
        self.read = "all"
        self.save()
    
    def __str__(self):
        return str(self.room + " : " + self.name + "-" + self.value)