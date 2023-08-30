from django.db import models
from django.contrib.auth.models import AbstractUser

from .utils import CITY_CHOICES


class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100, choices=CITY_CHOICES)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.PositiveIntegerField(default=0)

    def has_rated(self, user_id):
        """
        Проверяет, оценил ли текущий пользователь уже данного пользователя.
        """

        return Rating.objects.filter(rater=self, rated_id=user_id).exists()

    def rate_(self, rating, rated_user):
        """
        Метод для оценки пользователя другими пользователями.
        """
        if self.has_rated(rated_user.id):
            raise ValueError("Вы уже оценили этого пользователя")

        if 1 <= rating <= 5:
            rated_user.average_rating = (rated_user.average_rating * rated_user.total_ratings + rating) / (
                        rated_user.total_ratings + 1)
            rated_user.total_ratings += 1
            rated_user.save()
            Rating.objects.create(rater=self, rated_id=rated_user.id, rating=rating)
        else:
            raise ValueError("Рейтинг должен быть в диапазоне от 1 до 5")


class Rating(models.Model):
    rater = models.ForeignKey(User, on_delete=models.CASCADE)  # rater (Оценивающий):
    rated = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_ratings')  # rated (Оцениваемый)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ['rater', 'rated']
