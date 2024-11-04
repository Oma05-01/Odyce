# Generated by Django 5.1.1 on 2024-10-30 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_articles_contactus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='First_name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='customer',
            old_name='Last_name',
            new_name='last_name',
        ),
        migrations.AddField(
            model_name='contactus',
            name='message',
            field=models.TextField(default=''),
        ),
    ]
