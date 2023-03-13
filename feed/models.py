from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# for image compression
from io import BytesIO
from PIL import Image
from django.core.files import File

#image compression method
def compress(image):
    im = Image.open(image)
    im = im.convert('RGB')
    im_io = BytesIO() 
    im.save(im_io, 'JPEG', quality=60) 
    new_image = File(im_io, name=image.name)
    return new_image

class Post(models.Model):
    description = models.CharField(max_length=255, blank=True)
    pic = models.ImageField(upload_to='path/to/img')
    date_posted = models.DateTimeField(default=timezone.now)
    user_name = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.CharField(max_length=100, blank=True)

    #calling image compression function before saving the data
    def save(self, *args, **kwargs):
                new_image = compress(self.pic)
                self.pic = new_image
                super().save(*args, **kwargs)

    def __str__(self):
        return self.description


    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
 

class Comments(models.Model):
    post = models.ForeignKey(Post, related_name='details', on_delete=models.CASCADE)
    username = models.ForeignKey(User, related_name='details', on_delete=models.CASCADE)
    comment = models.CharField(max_length=255)
    comment_date = models.DateTimeField(default=timezone.now)

class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)	


