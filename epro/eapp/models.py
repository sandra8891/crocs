from django.db import models
from django.contrib.auth.models import User

# class Gallery(models.Model):
#     title1 = models.CharField(max_length=255)
#     title2 = models.CharField(max_length=255)
#     title3 = models.CharField(max_length=255)
#     feedimage = models.ImageField(upload_to='gallery_images/')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product=models.ForeignKey(Gallery, on_delete=models.CASCADE)


