# Generated by Django 4.2.2 on 2023-10-01 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bboard', '0024_alter_ordercart_options_message_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='receiver_unread',
            field=models.BooleanField(default=False, verbose_name='Непрочитанные сообщения получателя'),
        ),
        migrations.AddField(
            model_name='chat',
            name='sender_unread',
            field=models.BooleanField(default=False, verbose_name='Непрочитанные сообщения отправителя'),
        ),
    ]
