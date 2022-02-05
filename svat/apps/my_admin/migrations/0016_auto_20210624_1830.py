# Generated by Django 3.2.1 on 2021-06-24 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_admin', '0015_remove_product_quantity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='importorderproduct',
            name='product',
        ),
        migrations.AddField(
            model_name='importorderproduct',
            name='product_model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='my_admin.productmodel'),
        ),
    ]
