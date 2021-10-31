# Generated by Django 3.1.1 on 2021-10-31 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0002_widget'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('position', models.PositiveIntegerField()),
                ('message_sent', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('date', 'position'),
            },
        ),
    ]
