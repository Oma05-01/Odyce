# Generated by Django 5.1.1 on 2024-11-01 18:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0005_customer_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='quantity',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='content_type',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wishlistitem',
            name='object_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
