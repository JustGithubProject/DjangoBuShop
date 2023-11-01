from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, max_length=400, verbose_name="URL", blank=True)
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image_1 = models.ImageField(upload_to="products", null=True, blank=True, verbose_name="Первое изображение")
    image_2 = models.ImageField(upload_to='products', null=True, blank=True, verbose_name="Второе изображение")
    image_3 = models.ImageField(upload_to='products', null=True, blank=True, verbose_name="Третье изображение")
    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Дата создания")

    thumbnail_1 = ImageSpecField(source='image_1',
                                 processors=[ResizeToFill(500, 500)],
                                 format='JPEG',
                                 options={'quality': 100})

    thumbnail_2 = ImageSpecField(source='image_2',
                                 processors=[ResizeToFill(500, 500)],
                                 format='JPEG',
                                 options={'quality': 100})
    thumbnail_3 = ImageSpecField(source='image_3',
                                 processors=[ResizeToFill(500, 500)],
                                 format='JPEG',
                                 options={'quality': 100})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    customer_name = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    email = models.EmailField(verbose_name="Email", blank=True)
    name = models.CharField(max_length=100, null=True, verbose_name="Имя клиента")
    surname = models.CharField(max_length=100, null=True, verbose_name="Фамилия клиента")
    phone_number = models.CharField(max_length=50, null=True, verbose_name="Номер телефона")
    city = models.CharField(max_length=100, null=True, verbose_name="Населенный пункт")
    department = models.CharField(max_length=600, null=True, verbose_name="Отделение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Order #{self.pk}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderCart(models.Model):
    products = models.ManyToManyField(Product, verbose_name="Товар")
    customer_name = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    email = models.EmailField(verbose_name="Email", blank=True)
    name = models.CharField(max_length=100, null=True, verbose_name="Имя клиента")
    surname = models.CharField(max_length=100, null=True, verbose_name="Фамилия клиента")
    phone_number = models.CharField(max_length=50, null=True, verbose_name="Номер телефона")
    city = models.CharField(max_length=100, null=True, verbose_name="Населенный пункт")
    department = models.CharField(max_length=600, null=True, verbose_name="Отделение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Order cart #{self.pk}"

    class Meta:
        verbose_name = "Заказ с корзины"
        verbose_name_plural = "Заказы c корзины"


class Chat(models.Model):
    sender = models.ForeignKey(User, related_name='sent_chats', on_delete=models.CASCADE, null=True, verbose_name='Отправитель')
    receiver = models.ForeignKey(User, related_name='received_chats', on_delete=models.CASCADE, null=True, verbose_name='Получатель')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    last_message = models.ForeignKey('Message', null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='chat_messages', verbose_name='Последнее сообщение')

    def __str__(self):
        return f"Chat -> sender={self.sender}, receiver={self.receiver}, product={self.product}"

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE, verbose_name='Чат')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Отправитель')
    content = models.TextField(db_index=False, verbose_name='Содержание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    def __str__(self):
        return f"Message of {self.sender}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Review(models.Model):
    reviewer_name = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    content = models.TextField(verbose_name='Комментарий')
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return f"Пользователь - {self.reviewer_name} оставил комментарий"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    products = models.ManyToManyField(Product, through="CartItem", related_name='carts', verbose_name="Товары")

    def __str__(self):
        return f"Корзина пользователя {self.user}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product}"

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Получатель")
    id_invoice = models.CharField(max_length=10, verbose_name="Идентификатор экспресс-накладной")
    cost_on_site = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость доставки")
    estimated_delivery_date = models.CharField(max_length=60, verbose_name="Прогнозируемая дата доставки")
    int_doc_number = models.CharField(max_length=100, verbose_name="Номер экспресс-накладной")
    type_document = models.CharField(max_length=100, verbose_name="Тип экспресс-накладной")

