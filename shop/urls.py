from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('products/category/<str:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<str:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('order/create/', views.order_create, name='order_create'),
    path('my-ads/', views.my_ads, name='my_ads'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('search/autocomplete/', views.product_search_autocomplete, name='product_search_autocomplete'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/start/<int:product_id>/', views.start_chat, name='start_chat'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/password/', views.change_password, name='change_password'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),
]
