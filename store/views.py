from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Product, Cart, CartItem,OrderItem, Order


# =========================
# Trang chủ
# =========================
def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


# =========================
# Trang thông tin
# =========================
def about(request):
    return render(request, 'about.html')


# =========================
# Trang liên hệ
# =========================
def contact(request):
    return render(request, 'contact.html')


# =========================
# Chi tiết sản phẩm
# =========================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


# =========================
# Đăng nhập
# =========================
def login_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html')


# =========================
# Đăng ký
# =========================
def register_view(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        User.objects.create_user(username=username, password=password)

        return redirect('login')

    return render(request, 'register.html')


# =========================
# Đăng xuất
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# Thêm vào giỏ hàng
# =========================
@login_required
def add_to_cart(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    quantity = int(request.POST.get('quantity', 1))

    cart, created = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity

    item.save()

    return redirect('cart')


# =========================
# Trang giỏ hàng
# =========================
@login_required
def cart_view(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.product.price * item.quantity

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


# =========================
# Trang thanh toán
# =========================
@login_required
def checkout(request):

    cart, created = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.product.price * item.quantity

    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })
# =========================
# Lưu đơn hàng → Trang xác nhận đặt hàng
# =========================
@login_required
def checkout(request):

    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total = 0
    for item in items:
        total += item.product.price * item.quantity

    if request.method == "POST":

        name = request.POST['name']
        phone = request.POST['phone']
        address = request.POST['address']

        order = Order.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            address=address,
            total=total
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        items.delete()

        return redirect('order_success')

    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })
def order_success(request):
    return render(request, 'order_success.html')
# =========================
#Xóa giỏ hàng
# =========================
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')