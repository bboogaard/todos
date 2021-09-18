# Generated by Django 3.1.1 on 2021-09-18 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'ordering': ('position',)},
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={'ordering': ('activate_date',)},
        ),
        migrations.AddField(
            model_name='note',
            name='is_encrypted',
            field=models.BooleanField(default=False),
        ),
    ]
