# Generated by Django 4.2.2 on 2023-11-05 16:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bboard', '0027_remove_chat_receiver_unread_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_invoice', models.CharField(max_length=10, verbose_name='Идентификатор экспресс-накладной')),
                ('cost_on_site', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость доставки')),
                ('estimated_delivery_date', models.CharField(max_length=60, verbose_name='Прогнозируемая дата доставки')),
                ('int_doc_number', models.CharField(max_length=100, verbose_name='Номер экспресс-накладной')),
                ('type_document', models.CharField(max_length=100, verbose_name='Тип экспресс-накладной')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
            ],
        ),
    ]
