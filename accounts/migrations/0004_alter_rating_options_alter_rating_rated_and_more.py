# Generated by Django 4.2.2 on 2023-09-18 20:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rating'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rating',
            options={'verbose_name': 'Оценка', 'verbose_name_plural': 'Оценки'},
        ),
        migrations.AlterField(
            model_name='rating',
            name='rated',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_ratings', to=settings.AUTH_USER_MODEL, verbose_name='Оцениваемый'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='rater',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Оценивающий'),
        ),
        migrations.AlterField(
            model_name='rating',
            name='rating',
            field=models.PositiveIntegerField(verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='user',
            name='average_rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3, verbose_name='Средний рейтинг'),
        ),
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.CharField(choices=[('Kiev', 'Киев'), ('Kharkiv', 'Харьков'), ('Odessa', 'Одесса'), ('Dnipro', 'Днепр'), ('Lviv', 'Львов'), ('Kyiv', 'Київ'), ('Donetsk', 'Донецк'), ('Zaporizhzhia', 'Запорожье'), ('Khmelnytskyi', 'Хмельницкий'), ('Vinnytsia', 'Винница'), ('Zhytomyr', 'Житомир'), ('Chernihiv', 'Чернигов'), ('Cherkasy', 'Черкасы'), ('Sumy', 'Сумы'), ('Poltava', 'Полтава'), ('Rivne', 'Ровно'), ('Uzhhorod', 'Ужгород'), ('Mykolaiv', 'Николаев'), ('Ternopil', 'Тернополь'), ('Kherson', 'Херсон'), ('Ivano-Frankivsk', 'Ивано-Франковск'), ('Lutsk', 'Луцк'), ('Melitopol', 'Мелитополь'), ('Kropyvnytskyi', 'Кропивницкий'), ('Berdiansk', 'Бердянск'), ('Nikopol', 'Никополь'), ('Kremenchuk', 'Кременчуг'), ('Simferopol', 'Симферополь'), ('Brovary', 'Бровары'), ('Khmelnitsky', 'Хмельницкий'), ('Pavlohrad', 'Павлоград'), ('Chernivtsi', 'Черновцы')], max_length=100, verbose_name='Населенный пункт'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='user',
            name='total_ratings',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество оценок'),
        ),
    ]
