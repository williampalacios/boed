# Generated by Django 2.2.7 on 2019-11-22 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20191122_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
