# Generated by Django 2.1.7 on 2019-02-12 23:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20190212_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='parent_location',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='main.Location'),
        ),
    ]
