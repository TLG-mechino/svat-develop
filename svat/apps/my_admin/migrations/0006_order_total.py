# Generated by Django 3.2.1 on 2021-06-04 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_admin', '0005_order_shipping_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.IntegerField(default=0),
        ),
    ]
