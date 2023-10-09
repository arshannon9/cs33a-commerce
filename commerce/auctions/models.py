from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=100)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.ImageField(
        upload_to='listings/', height_field=None, width_field=None, max_length=100)
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name='listings')


class Bid(models.Model):
    bidder = models.FoerignKey(
        'User', on_delete=models.CASCADE, related_name='bids')
    listing = models.ForeignKey(
        'Listing', on_delete=models.CASCADE, related_name='listings')
    bid_amount = models.DecimalField(max_digits=12, decimal_places=2)


class Comment(models.Model):
    bidder = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='comments')
    listing = models.ForeignKey(
        'Listing', on_delete=models.CASCADE, related_name='listings')
    comment = models.TextField()


class Category(models.Model):
    name = models.CharField(max_length=40)
