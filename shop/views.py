import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Category, Product, Order, OrderItem, Favorite, ProductImage, Chat, Message
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.text import slugify
from .forms import ProductForm, UserRegistrationForm, UserEditForm
from .services import ProductService


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = ProductService.create_product(request.user, form, request.FILES)
            messages.success(request, 'Ваше объявление успешно размещено!')
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form, 'title': 'Разместить объявление'})

@login_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            ProductService.update_product(product, form, request.FILES)
            messages.success(request, 'Объявление успешно обновлено!')
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/product_form.html', {'form': form, 'product': product, 'title': 'Редактировать объявление'})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт {user.username} успешно создан! Добро пожаловать!')
            return redirect('shop:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    recommended_products = Product.objects.filter(available=True).order_by('?')[:4]
    return render(request, 'shop/home.html', {'recommended_products': recommended_products})

from django.db.models import Q, F, Value, Func
from django.db.models.functions import Lower

from django.core.paginator import Paginator

def product_list(request, category_slug=None):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '')
    
    products_qs, category = ProductService.get_filtered_products(
        category_slug=category_slug,
        query=query,
        min_price=min_price,
        max_price=max_price,
        sort=sort
    )
    
    page_obj = ProductService.get_paginated_products(
        products_qs, 
        request.GET.get('page')
    )
    
    favorite_product_ids = []
    if request.user.is_authenticated:
        favorite_product_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': Category.objects.all(),
        'products': page_obj,
        'favorite_product_ids': favorite_product_ids,
        'current_sort': sort,
        'search_query': query
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()
    return render(request, 'shop/product_detail.html', {'product': product, 'is_favorite': is_favorite})

@login_required
def cart_detail(request):
    # Корзина полностью управляется на фронтенде через LocalStorage,
    # поэтому мы просто отдаем шаблон
    return render(request, 'shop/cart.html')

def order_create(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Сначала необходимо войти в аккаунт'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_info = data.get('user_info', {})
            cart = data.get('cart', [])

            if not cart:
                return JsonResponse({'error': 'Корзина пуста'}, status=400)

            order = Order.objects.create(
                buyer=request.user,
                first_name=user_info.get('first_name', request.user.first_name),
                last_name=user_info.get('last_name', request.user.last_name),
                email=user_info.get('email', request.user.email),
                address=user_info.get('address', ''),
                postal_code=user_info.get('postal_code', ''),
                city=user_info.get('city', '')
            )

            for item in cart:
                product = get_object_or_404(Product, id=item['product_id'])
                if product.owner == request.user:
                    return JsonResponse({'error': f'Вы не можете купить собственный товар: {product.name}'}, status=400)
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=item['price'],
                    quantity=item['quantity']
                )

            return JsonResponse({'message': 'Заказ успешно оформлен!', 'order_id': order.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)


@login_required
def my_purchases(request):
    """Shows all orders placed by the current user."""
    orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product').order_by('-created')
    return render(request, 'shop/my_purchases.html', {'orders': orders})

@login_required
@require_POST
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        favorite.delete()
        is_favorite = False
        message = 'Удалено из избранного'
    else:
        is_favorite = True
        message = 'Добавлено в избранное'

    return JsonResponse({
        'is_favorite': is_favorite,
        'message': message
    })

@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    products = [f.product for f in favorites]
    return render(request, 'shop/favorites_list.html', {'products': products})

@login_required
def my_ads(request):
    products = Product.objects.filter(owner=request.user).order_by('-created')
    return render(request, 'shop/my_ads.html', {'products': products})

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    products = Product.objects.filter(owner=user, available=True).order_by('-created')
    return render(request, 'shop/user_profile.html', {
        'profile_user': user,
        'products': products
    })


def product_search_autocomplete(request):
    query = request.GET.get('q', '')
    results = ProductService.get_autocomplete_results(query)
    return JsonResponse(results, safe=False)


@login_required
def chat_list(request):
    chats = Chat.objects.filter(Q(buyer=request.user) | Q(seller=request.user)).distinct()
    return render(request, 'shop/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.buyer != request.user and chat.seller != request.user:
        return redirect('shop:chat_list')
    
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            Message.objects.create(chat=chat, sender=request.user, text=text)
            chat.save() # Update updated_at
            return redirect('shop:chat_detail', chat_id=chat.id)
            
    messages = chat.messages.all()
    # Mark as read
    messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    return render(request, 'shop/chat_detail.html', {'chat': chat, 'chat_messages': messages})

@login_required
def start_chat(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if product.owner == request.user:
        return redirect('shop:product_detail', slug=product.slug)
    
    chat, created = Chat.objects.get_or_create(
        product=product,
        buyer=request.user,
        seller=product.owner
    )
    return redirect('shop:chat_detail', chat_id=chat.id)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('shop:user_profile', username=request.user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'shop/profile_edit.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep the user logged in
            messages.success(request, 'Ваш пароль успешно изменен!')
            return redirect('shop:user_profile', username=request.user.username)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'shop/change_password.html', {'form': form})
