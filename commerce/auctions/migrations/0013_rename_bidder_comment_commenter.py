# Generated by Django 4.2.5 on 2023-10-15 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_listing_winner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='bidder',
            new_name='commenter',
        ),
    ]
