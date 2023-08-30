from django.contrib import admin
from .models import User, Rating


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ('date_joined', 'is_active')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    pass