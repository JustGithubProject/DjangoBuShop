# Generated by Django 4.2.2 on 2023-08-18 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bboard', '0019_rename_customer_email_order_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='department',
            field=models.CharField(max_length=600, null=True),
        ),
    ]