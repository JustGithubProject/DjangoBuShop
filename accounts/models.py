from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import CITY_CHOICES


class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    def update_average_rating(self, new_rating):
        """
        Обновляет среднюю оценку пользователя при добавлении новой оценки.
        """
        self.average_rating = (self.average_rating * self.total_ratings + new_rating) / (self.total_ratings + 1)
        self.total_ratings += 1
        self.save()

    def rate(self, rating):
        """
        Метод для оценки пользователя другими пользователями.
        """
        if 1 <= rating <= 5:
            self.update_average_rating(rating)
        else:
            raise ValueError("Рейтинг должен быть в диапазоне от 1 до 5")

