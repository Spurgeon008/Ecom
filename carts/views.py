from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from store.models import Product

# Create your views here.
def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            cart_item.sub_total = cart_item.product.price * cart_item.quantity
            total += cart_item.sub_total
            quantity += cart_item.quantity
        tax = (2 * total)/100  # 2% tax
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass
        
    # Store cart count in session
    request.session['cart_count'] = quantity

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    try:
        # Get the cart using the cart_id present in the session
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        # Create a new cart
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    
    try:
        # Get the cart item
        cart_item = CartItem.objects.get(product=product, cart=cart, is_active=True)
        # Increment the cart item quantity if it already exists
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        # Create a new cart item if it doesn't exist
        if product.stock > 0:  # Only create if product is in stock
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            cart_item.save()
    
    # Update cart count in session
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    request.session['cart_count'] = sum(item.quantity for item in cart_items)
    
    # Redirect back to the product detail page
    return redirect(product.get_url())

def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id, is_active=True)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            
        # Update cart count in session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        request.session['cart_count'] = sum(item.quantity for item in cart_items)
        
    except CartItem.DoesNotExist:
        pass
    return redirect('cart')

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')