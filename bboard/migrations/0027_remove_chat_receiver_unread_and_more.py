# Generated by Django 4.2.2 on 2023-10-02 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bboard', '0026_remove_message_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chat',
            name='receiver_unread',
        ),
        migrations.RemoveField(
            model_name='chat',
            name='sender_unread',
        ),
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False, verbose_name='Прочитано'),
        ),
    ]
