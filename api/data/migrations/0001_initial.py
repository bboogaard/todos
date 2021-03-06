# Generated by Django 3.1.1 on 2022-04-24 14:38

from django.db import migrations, models
import private_storage.fields
import private_storage.storage.files


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CodeSnippet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(unique=True)),
                ('text', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('-position',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=100)),
                ('datetime', models.DateTimeField()),
            ],
            options={
                'ordering': ('datetime',),
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1, verbose_name='status')),
                ('activate_date', models.DateTimeField(blank=True, help_text='keep empty for an immediate activation', null=True)),
                ('deactivate_date', models.DateTimeField(blank=True, help_text='keep empty for indefinite activation', null=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('position', models.PositiveIntegerField(unique=True)),
                ('text', models.TextField(blank=True)),
            ],
            options={
                'ordering': ('-position',),
            },
        ),
        migrations.CreateModel(
            name='PrivateFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('file', private_storage.fields.PrivateFileField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='')),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrivateImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('image', private_storage.fields.PrivateImageField(storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='')),
            ],
            options={
                'ordering': ('-created',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1, verbose_name='status')),
                ('activate_date', models.DateTimeField(blank=True, help_text='keep empty for an immediate activation', null=True)),
                ('deactivate_date', models.DateTimeField(blank=True, help_text='keep empty for indefinite activation', null=True)),
                ('update_datetime', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ('-activate_date',),
            },
        ),
    ]
