from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=False)
    image = models.ImageField(
        upload_to=None, height_field=None, width_field=None, max_length=100)
    category = models.CharField(max_length=20)


class Bid(models.Model):
    pass


class Comment(models.Model):
    pass
