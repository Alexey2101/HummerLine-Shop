from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField('Название', max_length=200, db_index=True)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    owner = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField('Название', max_length=200, db_index=True)
    slug = models.SlugField('Slug', max_length=200, db_index=True)
    image = models.ImageField('Изображение', upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    phone_number = models.CharField('Номер телефона', max_length=20, blank=True, null=True)
    available = models.BooleanField('Доступно', default=True)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField('Изображение', upload_to='products/gallery/%Y/%m/%d')
    
    class Meta:
        verbose_name = 'Дополнительное изображение'
        verbose_name_plural = 'Дополнительные изображения'



class Order(models.Model):
    buyer = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Покупатель')
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    email = models.EmailField('Email')
    address = models.CharField('Адрес', max_length=250)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    city = models.CharField('Город', max_length=100)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлен', auto_now=True)
    paid = models.BooleanField('Оплачен', default=False)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name='Товар')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, related_name='favorited_by', on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='Товар')
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Рейтинг', choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-created_at',)

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.product.name}"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE, verbose_name='Отзыв')
    image = models.ImageField('Изображение', upload_to='reviews/%Y/%m/%d')

    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'

class ReviewLike(models.Model):
    review = models.ForeignKey(Review, related_name='likes', on_delete=models.CASCADE, verbose_name='Отзыв')
    user = models.ForeignKey(User, related_name='review_likes', on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')
        verbose_name = 'Лайк отзыва'
        verbose_name_plural = 'Лайки отзывов'

class Chat(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='chats')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_chats')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'buyer', 'seller')
        ordering = ['-updated_at']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return f"Чат по {self.product.name} между {self.buyer.username} и {self.seller.username}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField('Текст сообщения')
    created_at = models.DateTimeField('Дата отправки', auto_now_add=True)
    is_read = models.BooleanField('Прочитано', default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f"Сообщение от {self.sender.username} в {self.created_at}"


