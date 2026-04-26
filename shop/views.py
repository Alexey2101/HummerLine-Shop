import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, Favorite, ProductImage, Chat, Message, DeliveryCompany, EmailVerificationToken
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.text import slugify
from .forms import ProductForm, UserRegistrationForm, DeliveryCompanyRegistrationForm
from django.core.mail import send_mail
from django.conf import settings

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            
            # Генерация уникального slug
            base_slug = slugify(product.name, allow_unicode=True) or 'product'
            unique_slug = base_slug
            counter = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            product.slug = unique_slug
            product.save()

            # Сохранение дополнительных изображений галереи
            images = request.FILES.getlist('gallery')
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            messages.success(request, 'Ваше объявление успешно размещено!')
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm()
    return render(request, 'shop/product_form.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # disabled until email verified
            user.save()

            # Create verification token
            token_obj = EmailVerificationToken.objects.create(user=user)

            # Build verification URL
            verify_url = f"{settings.SITE_DOMAIN}/accounts/verify-email/{token_obj.token}/"

            # Send verification email
            send_mail(
                subject='Подтвердите ваш email — HummerLine',
                message=(
                    f"Привет, {user.username}!\n\n"
                    f"Спасибо за регистрацию на HummerLine.\n"
                    f"Для активации аккаунта перейдите по ссылке:\n\n"
                    f"{verify_url}\n\n"
                    f"Ссылка действительна 24 часа.\n\n"
                    f"Если вы не регистрировались на нашей платформе, просто проигнорируйте это письмо."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return redirect('shop:email_verification_sent')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def email_verification_sent(request):
    """Informational page shown right after registration."""
    return render(request, 'registration/email_verification_sent.html')


def activate_account(request, token):
    """Validates the UUID token and activates the user account."""
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(token=token)
    except EmailVerificationToken.DoesNotExist:
        return render(request, 'registration/email_verification_invalid.html',
                      {'reason': 'Ссылка недействительна или уже была использована.'})

    if token_obj.is_expired():
        token_obj.delete()
        return render(request, 'registration/email_verification_invalid.html',
                      {'reason': 'Ссылка истекла. Зарегистрируйтесь снова.'})

    user = token_obj.user
    user.is_active = True
    user.save()
    token_obj.delete()  # single-use token

    login(request, user)
    messages.success(request, f'Аккаунт {user.username} успешно активирован! Добро пожаловать!')
    return redirect('shop:home')

def home(request):
    return render(request, 'shop/home.html')

from django.db.models import Q, F, Value, Func
from django.db.models.functions import Lower

from django.core.paginator import Paginator

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Поиск
    query = request.GET.get('q')
    if query:
        query_lower = query.lower()
        # Сначала обычный поиск, потом нечеткий
        products = products.annotate(
            name_lower=Lower('name'),
            desc_lower=Lower('description'),
            similarity=Func(F('name'), Value(query), function='SIMILARITY')
        ).filter(
            Q(name_lower__contains=query_lower) | 
            Q(desc_lower__contains=query_lower) |
            Q(similarity__gt=0.3)
        ).order_by('-similarity', 'name_lower')
    
    # Фильтрация по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Сортировка
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name') # по умолчанию

    # Пагинация
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    favorite_product_ids = []
    if request.user.is_authenticated:
        favorite_product_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
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


def delivery_register(request):
    """Registration page for delivery/transport companies."""
    if request.user.is_authenticated and hasattr(request.user, 'delivery_company'):
        messages.info(request, 'Ваша компания уже зарегистрирована.')
        return redirect('shop:home')

    if request.method == 'POST':
        form = DeliveryCompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            DeliveryCompany.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                regions=form.cleaned_data['regions'],
                transport_types=form.cleaned_data['transport_types'],
                price_per_km=form.cleaned_data['price_per_km'],
                description=form.cleaned_data.get('description', ''),
                logo=form.cleaned_data.get('logo'),
            )
            login(request, user)
            messages.success(request, f'Компания «{form.cleaned_data["company_name"]}» успешно зарегистрирована!')
            return redirect('shop:home')
    else:
        form = DeliveryCompanyRegistrationForm()
    return render(request, 'shop/delivery_register.html', {'form': form})


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
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    query_lower = query.lower()
    products = Product.objects.filter(available=True).annotate(
        name_lower=Lower('name'),
        cat_lower=Lower('category__name'),
        similarity=Func(F('name'), Value(query), function='SIMILARITY')
    ).filter(
        Q(name_lower__contains=query_lower) | 
        Q(cat_lower__contains=query_lower) |
        Q(similarity__gt=0.3)
    ).order_by('-similarity')[:5]
    
    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'url': p.get_absolute_url(),
            'category': p.category.name,
            'image': p.image.url if p.image else None
        })
    
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
