# Generated by Django 3.2.7 on 2021-09-29 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newuser', '0003_auto_20210929_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='token',
            field=models.CharField(max_length=200),
        ),
    ]
