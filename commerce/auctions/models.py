from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'Listing', blank=True, related_name="users")


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(null=True)
    starting_bid = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    current_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    image = models.URLField(
        null=True, blank=True)
    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name='listings')
    is_active = models.BooleanField(default=True)
    listing_owner = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=True, related_name='listings')
    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)


class Bid(models.Model):
    bidder = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=True, related_name='bids')
    listing = models.ForeignKey(
        'Listing', on_delete=models.CASCADE, null=True, related_name='bids')
    bid_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)


class Comment(models.Model):
    commenter = models.ForeignKey(
        'User', on_delete=models.CASCADE, null=True, related_name='comments')
    listing = models.ForeignKey(
        'Listing', on_delete=models.CASCADE, null=True, related_name='comments')
    comment = models.TextField(null=True)


class Category(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name
