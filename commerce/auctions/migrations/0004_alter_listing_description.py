# Generated by Django 4.2.5 on 2023-10-09 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_category_bid_bid_amount_bid_bidder_bid_listing_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(null=True),
        ),
    ]