# Generated by Django 4.2.2 on 2023-07-20 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bboard', '0015_alter_order_customer_name_alter_product_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
