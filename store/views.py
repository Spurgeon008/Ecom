from django.shortcuts import render, get_object_or_404
from .models import Product 
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q

def store(request, category_slug=None):
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
        product_count = products.count()
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        product_count = products.count()
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        
        # Get variations for the product
        variations = single_product.variation_set.all()
        
        # Group variations by category
        variations_dict = {}
        for variation in variations:
            if variation.variation_category not in variations_dict:
                variations_dict[variation.variation_category] = []
            variations_dict[variation.variation_category].append(variation)
            
    except Exception as e:
        raise e

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'variations': variations_dict,
    }
    
    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword )| Q(product_name__icontains = keyword))
            product_count = products.count()
    context={
        'products':products,
        'product_count':product_count,
         }
    return render(request,'store/store.html',context)