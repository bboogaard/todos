# Generated by Django 3.1.1 on 2021-12-23 21:47

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('todos', '0003_event'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={},
        ),
        migrations.AlterModelOptions(
            name='todo',
            options={},
        ),
        migrations.AddField(
            model_name='event',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='note',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='privatefile',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='privatefile',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='todo',
            name='update_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
    ]