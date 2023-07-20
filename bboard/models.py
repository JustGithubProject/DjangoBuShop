from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True, max_length=400, verbose_name="URL")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_1 = models.ImageField(upload_to="products", null=True, blank=True)
    image_2 = models.ImageField(upload_to='products', null=True, blank=True)
    image_3 = models.ImageField(upload_to='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    thumbnail_1 = ImageSpecField(source='image_1',
                                 processors=[ResizeToFill(200, 200)],
                                 format='JPEG',
                                 options={'quality': 100})
    thumbnail_2 = ImageSpecField(source='image_2',
                                 processors=[ResizeToFill(200, 200)],
                                 format='JPEG',
                                 options={'quality': 100})
    thumbnail_3 = ImageSpecField(source='image_3',
                                 processors=[ResizeToFill(200, 200)],
                                 format='JPEG',
                                 options={'quality': 100})

    def __str__(self):
        return self.title


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    customer_name = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_email = models.EmailField()
    shipping_address = models.TextField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk}"


class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_chats', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User, related_name='received_chats', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message = models.ForeignKey('Message', null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='chat_messages')

    def __str__(self):
        return f"Chat -> sender={self.sender}, receiver={self.receiver}, product={self.product}"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, verbose_name='chat_message')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message of {self.sender}"
