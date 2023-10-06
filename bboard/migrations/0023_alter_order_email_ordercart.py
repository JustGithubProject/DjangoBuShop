# Generated by Django 4.2.2 on 2023-09-24 07:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bboard', '0022_cart_alter_category_options_alter_chat_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Email'),
        ),
        migrations.CreateModel(
            name='OrderCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('name', models.CharField(max_length=100, null=True, verbose_name='Имя клиента')),
                ('surname', models.CharField(max_length=100, null=True, verbose_name='Фамилия клиента')),
                ('phone_number', models.CharField(max_length=50, null=True, verbose_name='Номер телефона')),
                ('city', models.CharField(max_length=100, null=True, verbose_name='Населенный пункт')),
                ('department', models.CharField(max_length=600, null=True, verbose_name='Отделение')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('customer_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
                ('products', models.ManyToManyField(to='bboard.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
    ]