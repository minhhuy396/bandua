from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from .models import Product, Cart, CartItem, OrderItem, Order, Category


# =========================
# Trang chủ
# =========================
def home(request):

    products = Product.objects.all()

    categories = Category.objects.filter(parent=None)

    return render(request,'home.html',{
        'products':products,
        'categories':categories
    })

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
# Checkout + tạo đơn hàng + gửi email
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

        message = f"""
📦 Có đơn hàng mới từ website

Tên khách: {name}
SĐT: {phone}
Địa chỉ: {address}

Sản phẩm:
"""

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            message += f"- {item.product.name} x {item.quantity}\n"

        message += f"\n💰 Tổng tiền: {total} đ"

        # gửi email
        send_mail(
            "📦 Đơn hàng mới",
            message,
            settings.EMAIL_HOST_USER,
            ["nmhuy396@gmail.com"],
            fail_silently=False,
        )

        items.delete()

        return redirect('order_success')

    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })


# =========================
# Trang đặt hàng thành công
# =========================
def order_success(request):
    return render(request, 'order_success.html')


# =========================
# Xóa sản phẩm khỏi giỏ
# =========================
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')
# =========================
# Sản phẩm theo danh mục
# =========================
def category_products(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    products = Product.objects.filter(category=category)

    categories = Category.objects.all()

    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'selected_category': category
    })