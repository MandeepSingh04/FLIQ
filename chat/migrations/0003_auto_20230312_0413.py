# Generated by Django 3.2 on 2023-03-11 22:43

import autoslug.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_message_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='image',
            field=models.ImageField(default='default.png', upload_to='profile_pics'),
        ),
        migrations.AddField(
            model_name='message',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='slug',
            field=autoslug.fields.AutoSlugField(default=django.utils.timezone.now, editable=False, populate_from='user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='message',
            name='username',
            field=models.CharField(default=django.utils.timezone.now, max_length=1000000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='message',
            name='room',
            field=models.CharField(max_length=10000000),
        ),
    ]
