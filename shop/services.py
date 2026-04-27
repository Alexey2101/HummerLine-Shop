from django.db.models import Q, F, Value, Func
from django.db.models.functions import Lower
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Product, Category, ProductImage, Favorite

class ProductService:
    @staticmethod
    def get_filtered_products(category_slug=None, query=None, min_price=None, max_price=None, sort=None):
        """
        Filters products based on category, search query, price range and sorting.
        """
        products = Product.objects.filter(available=True)
        category = None

        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                products = products.filter(category=category)
            except Category.DoesNotExist:
                pass

        if query:
            query_lower = query.lower()
            products = products.annotate(
                name_lower=Lower('name'),
                desc_lower=Lower('description'),
                similarity=Func(F('name'), Value(query), function='SIMILARITY')
            ).filter(
                Q(name_lower__contains=query_lower) | 
                Q(desc_lower__contains=query_lower) |
                Q(similarity__gt=0.3)
            ).order_by('-similarity', 'name_lower')

        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        elif sort == 'newest':
            products = products.order_by('-created')
        elif not query:
            products = products.order_by('name')

        return products, category

    @staticmethod
    def get_paginated_products(products, page_number, per_page=9):
        paginator = Paginator(products, per_page)
        return paginator.get_page(page_number)

    @staticmethod
    def get_autocomplete_results(query, limit=5):
        if len(query) < 2:
            return []
        
        query_lower = query.lower()
        products = Product.objects.filter(available=True).annotate(
            name_lower=Lower('name'),
            cat_lower=Lower('category__name'),
            similarity=Func(F('name'), Value(query), function='SIMILARITY')
        ).filter(
            Q(name_lower__contains=query_lower) | 
            Q(cat_lower__contains=query_lower) |
            Q(similarity__gt=0.3)
        ).order_by('-similarity')[:limit]
        
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
        return results

    @staticmethod
    def create_product(user, form, files):
        """
        Creates a product, generates a unique slug and saves gallery images.
        """
        product = form.save(commit=False)
        product.owner = user
        
        # Generate unique slug
        base_slug = slugify(product.name, allow_unicode=True) or 'product'
        unique_slug = base_slug
        counter = 1
        while Product.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
        product.slug = unique_slug
        product.save()

        # Save gallery images
        gallery_images = files.getlist('gallery')
        for image in gallery_images:
            ProductImage.objects.create(product=product, image=image)
        
        return product

    @staticmethod
    def update_product(product, form, files):
        """
        Updates an existing product and optionally adds new gallery images.
        """
        product = form.save()
        
        # Save new gallery images if any
        gallery_images = files.getlist('gallery')
        for image in gallery_images:
            ProductImage.objects.create(product=product, image=image)
            
        return product
