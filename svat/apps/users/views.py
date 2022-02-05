from apps.my_admin.models import ProductCategory, Product, ProductImage, User, Media, Article, ArticleCategory,Order, OrderProduct , Message, ProductLanguage, ProductModel
from django.contrib.auth import login, authenticate, logout
from django.template.loader import render_to_string
from django.utils.translation import activate, ugettext as _ 
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render
from django.db import transaction
from django.conf import settings
from django.http import Http404
from django.db.models import F
from django.db.models import Q
import random
import string
import json
from django.http.response import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder


def index(request):
    product_categories = ProductCategory.objects.all()
    feature_products = Product.objects.all().order_by('-view')[:12]
    lastest_products = Product.objects.all().order_by('-id')[:12]
    newest_articles = Article.objects.all().order_by('post_at')[:4]
    return render(request, 'user/pages/index.html',{
        "product_categories": product_categories,
        "feature_products": feature_products,
        "lastest_products": lastest_products,
        "newest_articles": newest_articles,
    })


def handle_register (request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = User.objects.filter(email=data['email']).first();
        if user is not None:
            return JsonResponse({
                'success': False,
                'errors': [{
                    'email': "Email đã được đăng kí" 
                }]
            })

        # 1. Save User
        user = User()
        user.name = data['name']
        user.email = data['email']
        user.username = data['email']
        user.set_password(data['password'])
        user.verified_token = ''.join(random.choice(''.join((string.ascii_letters, string.digits))) for _ in range(32))
        user.phone_number = data['phone_number']
        user.save()

        # 2. Send verify email
        try:
            send_activate_email(user)
        except TimeoutError as e:
            return JsonResponse({
                'success': False,
                'errors': [{
                    "server":_("forget-password-timeout")
                }]
            })

        return JsonResponse({
            'success': True,
        })
    if request.method == "GET":
        if not request.user.is_authenticated:
            return render(request, 'user/pages/register/register.html')
        return redirect('user.index')

def send_activate_email (user):
    subject = '[SVAT] Kích hoạt tài khoản'
    msg_html = render_to_string('user/pages/register/register-email-form.html', { 'user': user })
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, msg_html, email_from, recipient_list, html_message=msg_html)


def send_reset_password_email (request, user):
    secret_token = ''.join(random.choice(''.join((string.ascii_letters, string.digits))) for _ in range(6))
    request.session['secret-token'] = secret_token
    request.session.modified = True
    subject = '[SVAT] Khôi phục mật khẩu'
    msg_html = render_to_string('user/pages/forgot-password/forgot-password-email-form.html', { 'user': user , 'secret_token': secret_token})
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, msg_html, email_from, recipient_list, html_message=msg_html)


def verify_email (request, email, verify_token):
    user = User.objects.filter(email=email, verified_token=verify_token).first()
    if user:
        if user.is_verify == 0:
            user.is_verify = 1
            user.save()
            login(request, user)
            return render(request, 'user/pages/index.html')
        else:
            raise Http404("Invalid Token")
    else:
        raise Http404("Invalid Token")


def success_register (request):
    if request.GET.get('email', None) is not None:
       email = request.GET.get('email') 
       return render(request, "user/pages/register/success-register.html", {'email': email})
       

def resend_activate (request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        if email is None:
            return JsonResponse({
                "success": False,
                "errors": "No email provided"
            })
        user = User.objects.filter(email=email).first()
        if user is None:
            return JsonResponse({
                "success": False,
                "errors": "Email is not valid"
            })

        try:
            send_activate_email(user)
        except TimeoutError as e:
            return JsonResponse({
                'success': False,
                'errors': "Lỗi Server"
            })

        return JsonResponse({
            "success": True,
            "errors": ""
        })


def handle_login (request):
    if request.user.is_authenticated:
        return redirect('user.index')

    if request.method == "POST":
        email = request.POST.get("email", None)
        password = request.POST.get("password", None)
        user = authenticate(username=email, password=password)
        if user:
            if user.is_verify == 0:
                # Not activate email
                return render(request, 'user/pages/forgot-password/re-verify-email.html', {'email': email})
            else:
                # login success
                login(request, user)
                return redirect('user.index')
        else:
            # Wrong credential
            return render(request, 'user/pages/login.html', {'errors': _('login-validate')})
    else:
        context = {}
        if "success" in request.GET:
            context['success'] = request.GET.get('success', None)
        return render(request, 'user/pages/login.html', context)


def handle_logout (request):
    if request.user.is_authenticated:
        logout(request)
    return redirect("user.index")


def forget_password (request):
    if request.method == "GET":
        return render(request, 'user/pages/forgot-password/forgot-password.html')


def forget_password_send_mail (request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = User.objects.filter(email=data['email']).first()
        if user is None:
            return JsonResponse({
                "success": False,
                "errors": _("forget-password-email-not-exits")
            })
        
        try:
            send_reset_password_email(request, user)
        except TimeoutError as e: 
            return JsonResponse({
                "success": False,
                "errors": _("forget-password-timeout")
            })

        return JsonResponse({
            'success': True,
            'errors': ""
        })


def forget_password_check_secret_token (request):
    if request.method == "POST":
        data = json.loads(request.body)
        secret_token = data['secret-token']
        
        if secret_token.strip() != request.session.get('secret-token', False):
            return JsonResponse({
                "success": False,
                "errors": _("forget-password-secret-token-not-valid")
            })

        return JsonResponse({
            'success': True,
            'errors': ""
        })


def forget_password_change_password(request):
    if request.method == "POST":
        data = json.loads(request.body)

        email = data['email']
        secret_token = data['secret-token']
        new_password = data['new-password']

        user = User.objects.filter(email=email).first()
        if user is None:
            return JsonResponse({
                "success": False,
                "errors": _("forget-password-email-not-exits")
            })

        if secret_token.strip() != request.session.get('secret-token', False):
            return JsonResponse({
                "success": False,
                "errors": _("forget-password-secret-token-not-valid")
            })

        user.set_password(new_password)
        # Active user too!
        user.is_verify = 1
        user.save()

        return JsonResponse({
            'success': True,
            'errors': ""
        })


def get_products_by_category(category_id, except_id=1, limit=4):
    products = Product.objects.filter(product_category=category_id).exclude(id=except_id)[:limit]
    return products


def detail_product(request, id):
    langCode = request.get_full_path().split('/')[1]

    product = Product.objects.filter(id=id).first()
    if not product:
        return render(request, "user/pages/404.html")
    product.view=product.view+1
    total_quantity = product.total_quantity()
    product.save()
    product_images = ProductImage.objects.filter(product=product).all()
    images = []
    for ele in product_images:
        image = Media.objects.filter(id=ele.media_id).first()
        images.append(image.__dict__)

    data = product.__dict__
    data['total_quantity'] = total_quantity
    data['images'] = images

    if langCode == 'vi':
        data['name'] = product.product_language_vi().name
        data['des'] = product.product_language_vi().des
    elif langCode == 'en':
        data['name'] = product.product_language_en().name
        data['des'] = product.product_language_en().des

    related_products = get_products_by_category(product.product_category, except_id=product.id)

    models = ProductModel.objects.filter(product=product).values('id', 'weight', 'price', 'quantity')
    models_json = json.dumps(list(models), cls=DjangoJSONEncoder)

    return render(request, "user/pages/product/detail.html", {"product": data, "related_products": related_products, "models": models, "models_json": models_json})


def get_product_list (request):
    if request.method == "GET":
        sort = request.GET.get('sort', None) 
        category_filter = request.GET.get('category', None) 
        keyword = request.GET.get('search_keyword', None) 

        category = None
        products = Product.objects

        # Filter
        if category_filter is not None:
            products = Product.objects.filter(product_category=category_filter)
            category = ProductCategory.objects.filter(pk=category_filter).first()

        products = products.all()
        if keyword is not None:
            # Subquery
            ids = ProductLanguage.objects.filter(Q(des__icontains=keyword) | Q(name__icontains=keyword)).values_list('product_id', flat=True)
            products = products.filter(pk__in=list(ids))
            
        # Order
        if sort == None or sort == "lastest":
            products = products.order_by('-id')
        elif sort == "best-seller":
            products = products.order_by('-view') # Fix me
        elif sort == "price-desc":
            products = products.order_by('-view') # Fix me
        elif sort == "price-asc":
            products = products.order_by('-view') # Fix me

        # Categories
        categories = ProductCategory.objects.all()
        context = {
            "products": products[:20],
            "categories": categories,
            "category": category,
            "sort": sort,
        }
        return render(request, "user/pages/products.html", context)


def get_product_categories (request):
    product_categories = ProductCategory.objects.all()
    product_categories = serializers.serialize('json', list(product_categories), fields=('id', 'name_en', 'name_vi'))

    if request.is_mobile:
        article_categories = ArticleCategory.objects.all()
        article_categories= serializers.serialize('json', list(article_categories), fields=('id', 'name_en', 'name_vi'))

        return JsonResponse({
            "product_categories": product_categories,
            "article_categories": article_categories
        })

    return JsonResponse({
        "product_categories": product_categories,
    })


def get_article_list (request):
    category_filter = request.GET.get('category', None) 
    # Filter
    if category_filter is not None:
        articles = Article.objects.filter(article_category=category_filter)
        category = ArticleCategory.objects.filter(pk=category_filter).first()
    else:
        category = None
        articles = Article.objects.all()

    articles = articles.order_by('-post_at')
    categories = ArticleCategory.objects.all()
    most_view_articles = Article.objects.all().order_by('-view')

    context = {
        'most_view_articles': most_view_articles[:10],
        'articles': articles[:20],
        'categories': categories,
        'category': category,
    }

    return render(request, 'user/pages/articles.html', context)


def view_profile(request):
    if request.user.is_authenticated:
        user=User.objects.get(id=request.user.id)
        if user.dob != None:
            user.dob=str(user.dob.date())
        return render(request, "user/pages/profile.html",{"user":user})
    else:
        return redirect('/')


def update_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            data = json.loads(request.body)
            email=data['email']
            user=User.objects.get(email=email)
            if data['status_update']==0:
                if data['fullname'] != None:
                    user.name=data['fullname']
                if data['phone'] != None:
                    user.phone_number=data['phone']
                if data['address'] != None:
                    user.address=data['address']
                if data['dob'] != "":
                    user.dob=data['dob']
                else:
                    user.dob=None
                user.save()
            else:
                new_password=data['new_password']
                user.set_password(new_password)
                if data['fullname'] != None:
                    user.name=data['fullname']
                if data['phone'] != None:
                    user.phone_number=data['phone']
                if data['address'] != None:
                    user.address=data['address']
                if data['dob'] != "":
                    user.dob=data['dob']
                else:
                    user.dob=None
                user.save()
            data={
                "success":True,
            }
            return JsonResponse({
                "success": True,
            })


# Order
def view_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user_id=request.user.id).order_by("-id")
        for order in orders:
            order.created=order.created.strftime("%H:%M - %d/%m/%Y")
        return render(request, "user/pages/orders.html",{
            "orders": orders,
        })
    else:
        return redirect('/')


def delete_orders(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            order_id = json.loads(request.body)['id']
            order=Order.objects.get(id=order_id)
            order.status=4
            order.save()
            data={
                'success':True,
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        else:
            data={
                'success':False,
            }
            return HttpResponse(json.dumps(data), content_type='text/json')

    else:
        data={
            'success':False,
        }
        return HttpResponse(json.dumps(data), content_type='text/json')


def shopping_cart (request):
    if request.method == "GET":
        products = request.session.get('products_cart', [])
        
        result, total = prepare_cart_data(products)
        return render(request, "user/pages/checkout/shopping-cart.html", {
            "products": result,
            "total": total
        })

def prepare_cart_data (products):
    result = []
    total = 0
    for product in products:
        product_data = Product.objects.filter(pk=product['product_id']).first()
        product_model = ProductModel.objects.filter(pk=product['product_model_id']).first()
        result.append({
            "product": product_data,
            "product_model": product_model,
            "quantity": product['quantity']
        })
        total += int(product_model.price) * int(product['quantity'])
    return result, total


def get_shopping_cart (request):
    return JsonResponse({
        'total': len(request.session.get('products_cart', []))
    })


def add_product_to_cart (request):
    if request.method == "POST":
        data = json.loads(request.body)
        current_cart = request.session.get('products_cart', [])
        
        # Check if exists
        product_in_cart = list(filter(lambda item: int(item['product_model_id']) == int(data['product_model_id']), current_cart))
        if len(product_in_cart) > 0:
            product_in_cart = product_in_cart[0]
            if int(product_in_cart['quantity']) == int(data['quantity']):
                # product in cart already
                return JsonResponse({
                    'success': False,
                    'message': _("shopping-cart-alert-fail-01")
                })
            else:
                # Update quantity
                index = current_cart.index(product_in_cart)
                current_cart[index] = data
                request.session['products_cart'] = current_cart
                return JsonResponse({
                    'success': True,
                    'message': _("shopping-cart-alert-success-01"),
                    'data': {
                        "total": len(current_cart)
                    }
                })
        else:
            # Add product to cart 
            current_cart.append(data)
            request.session['products_cart'] = current_cart
            return JsonResponse({
                'success': True,
                'message': _("shopping-cart-alert-success-02"),
                'data': {
                    "total": len(current_cart)
                }
            })


def update_product_to_cart (request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session['products_cart'] = data
        return JsonResponse({
            'success': True,
        })


def delete_product_to_cart (request):
    if request.method == "DELETE":
        data = json.loads(request.body)
        current_cart = request.session.get('products_cart', [])
        product_in_cart = list(filter(lambda item: int(item['product_id']) != int(data['product_id']), current_cart))

        request.session['products_cart'] = product_in_cart
        return JsonResponse({
            'success': True,
        })


# Contact
def contact(request):
    return render(request, 'user/pages/contact.html')

def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        new_mess=Message(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        new_mess.save()
        data={
            "success":True,
        }
        return JsonResponse({
            "success": True,
        })

        
@transaction.atomic
def checkout (request):
    if request.method == "GET":
        # Get checkout first
        products = request.session.get('checkout_now', [])
        # Reset checkout
        request.session['checkout_now'] = []
        if len(products) == 0:
            products = request.session.get('products_cart', [])
        
        if len(products) == 0:
            return redirect("user.shopping_cart")
        
        result, total = prepare_cart_data(products)
        return render(request, 'user/pages/checkout/checkout.html', {
            "products": result,
            "total": total
        })

    if request.method == "POST":
        data = json.loads(request.body)
        order = Order()
        order.address = data['address']
        order.name = data['name']
        order.email = data['email']
        order.phone_number = data['phone_number']
        order.note = data['note']
        order.status = 0
        order.total = 0
        order.total_products = 0
        order.shipping_fee = 0

        if request.user.is_authenticated:
            order.user = request.user
        else:
            user = User.objects.filter(email=data['email']).first()
            if user is None:
                if 'password' in data:
                    user = User()
                    user.name = data['name']
                    user.email = data['email']
                    user.username = data['email']
                    user.set_password(data['password'])
                    user.verified_token = ''.join(random.choice(''.join((string.ascii_letters, string.digits))) for _ in range(32))
                    user.phone_number = data['phone_number']
                    user.save()

                    # 2. Send verify email
                    try:
                        send_activate_email(user)
                    except TimeoutError as e:
                        return JsonResponse({
                            'success': False,
                            'errors': [{
                                "server":_("forget-password-timeout")
                            }]
                        })

                    order.user = user
                else:
                    # no user provided
                    pass
        order.save()

        total = 0
        for product in data['products']:
            product_model_data = ProductModel.objects.filter(pk=product['product_model_id']).first()
            product_model_data.quantity = product_model_data.quantity - product['quantity']
            product_model_data.save()

            order_product = OrderProduct()
            order_product.quantity = product['quantity']
            order_product.order = order
            order_product.product_model = product_model_data
            total += int(product_model_data.price) * int(product['quantity'])
            order_product.save()

        order.total_products = total
        order.shipping_fee = 0
        order.total = total
        order.save()

        # reset cart to zero
        request.session['products_cart'] = []

        return JsonResponse({
            'success': True,
            'message': ""
        })

# Article detail
def get_articles_by_category(category_id, except_id=1, limit=4):
    articles = Article.objects.filter(article_category=category_id).exclude(id=except_id)[:limit]
    return articles

def get_newest_articles(limit=4):
    articles = Article.objects.all().order_by('post_at')[:4]
    return articles

def detail_article(request, id):
    article = Article.objects.filter(id=id).first()
    if not article:
        return render(request, "user/pages/404.html")

    langCode = request.get_full_path().split('/')[1]
    categories = []

    if langCode == 'vi':
        categories = ArticleCategory.objects.all().values('id', 'name_vi').annotate(name=F('name_vi'))
    elif langCode == 'en':
        categories = ArticleCategory.objects.all().values('id', 'name_en').annotate(name=F('name_en'))

    related_articles = get_articles_by_category(article.article_category, except_id=article.id)
    newest_articles = get_newest_articles()
    article.view=article.view+1
    article.save()
    return render(request, "user/pages/article/detail.html", 
                  {"article": article, "categories": categories, "related_articles": related_articles, "newest_articles": newest_articles})

def checkout_now (request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Set new card
        request.session['checkout_now'] = [data]
        
        return JsonResponse({
            'success': True,
            'message': ""
        })
