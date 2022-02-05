from django.db.models.expressions import Case, Func, Value, When
from apps.my_admin.models import Article, Language, ArticleCategory, User, ProductCategory, Media, ArticleLanguage, ProductImage, ProductLanguage, Product, Order, OrderProduct,ProductLanguage,ImportOrderProduct,ImportOrder, Message, ProductModel
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.core.files.base import ContentFile
from apps.my_admin.forms import ArticleForm, ProductForm
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.db.models import Count, Q, F
from django.conf import settings
from datetime import datetime
from django.db import transaction
from django.http import Http404
from pathlib import Path

import apps.my_admin.permissions as PERMISSIONS
import time
import json
import os


# Dashboard
def index(request):
    total_order = len(Order.objects.all())
    total_product = len(Product.objects.all())
    total_user = len(User.objects.all())
    total_feed_back = len(Message.objects.all())
    list_category = Product.objects.all().values('product_category__name_vi', 'product_category_id').annotate(total=Count('product_category_id'))
    context = {
        "total_order": total_order, 
        "total_product": total_product, 
        "total_user": total_user, 
        "total_feed_back": total_feed_back,
        "list_category": list_category
    }
    return render(request, 'pages/dashboard.html', context)


# Login
def handle_login(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user = authenticate(request, password=password, username=email)
        if user is None:
            return render(request, 'pages/login.html', {'error': "Sai email hoặc mật khẩu"})
        if user.role not in [10, 11, 12, 13]:
            return render(request, 'pages/login.html', {'error': "User không có quyền truy cập tài nguyên"})
        else:
            login(request, user)
            return redirect('admin.dashboard')
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('admin.dashboard')
        else:
            return render(request, 'pages/login.html')


# Logout
def handle_logout(request):
    if request.method == 'POST':
        logout(request)
        return render(request, 'pages/login.html')


def handle403(request):
    return render(request, 'pages/403.html')



def paginate(params, Model, values, initial_query=Q(), search_fields=[], order_fields=[]):
    instances = Model.objects.filter(initial_query).values(*values).order_by(*order_fields)

    # Process keyword searching
    search_keyword = params.get('search[value]', '')
    if search_keyword:
        query = None
        for ele in search_fields:
            kwarg = {f"{ele}__icontains": search_keyword}
            if query is None:
                query = Q(**kwarg)
            else:
                query.add(Q(**kwarg), Q.OR)

        instances = Model.objects.filter(initial_query, query).values(*values).order_by(*order_fields)

    # Pagination
    records_per_page = int(params.get('length', 20))
    paginator = Paginator(instances, records_per_page)

    page_num = int(params.get('start', 1))
    if page_num < 1:
        page_num = 1
    elif page_num > paginator.num_pages:
        page_num = paginator.num_pages

    responses = paginator.page(page_num).object_list
    data = {
        "draw": params.get('draw', 0),
        "recordsTotal": paginator.count,
        "recordsFiltered": paginator.count,
        "data": list(responses),
    }
    return data


# User below
@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def user(request):
    return render(request, 'pages/user.html')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_user(request):
    if request.method == 'GET':
        values = ['id', 'name', 'phone_number', 'gender', 'email', 'role', 'dob']
        data = paginate(request.GET, User, values, search_fields=['email', 'name'])
        return JsonResponse(data, safe=False)


def is_valid_newuser(user):
    exist_email = User.objects.filter(email=user.email).exists()
    if exist_email:
        return False, "Email đã tồn tại"
    if not user.role:
        return False, "Role không thể để trống"
    if not user.email:
        return False, "Email không thể bỏ trống"
    return True, None


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def create_user(request):
    if request.method == 'POST':
        user = json.loads(request.body)
        # User.objects.create(**user)
        newUser = User(
            name=user['name'],
            dob=datetime.strptime(
                user['dob'], '%Y-%m-%d') if user['dob'] != '' else None,
            gender=int(user['gender']),
            email=user['email'],
            phone_number=user['phone_number'],
            role=user['role']
        )

        check, msg = is_valid_newuser(newUser)
        if check:
            newUser.save()

        data = {
            "success": check,
            "msg": msg
        }

        return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def update_user(request):
    if request.method == "POST":
        user = json.loads(request.body)
        user_in_db = User.objects.get(id=user['id'])
        for k, v in user.items():
            if k == 'dob':
                dob = datetime.strptime(
                    v, '%Y-%m-%d') if user['dob'] != '' else None
                setattr(user_in_db, k, dob)
            else:
                setattr(user_in_db, k, v)
        try:
            user_in_db.save()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as error:
            print(error)
            data = {
                "success": False,
                "msg": "Error when update database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def delete_user(request):
    if request.method == "POST":
        user = json.loads(request.body)
        try:
            User.objects.filter(id=user['id']).delete()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as e:
            print(e)
            data = {
                "success": False,
                "msg": "Error when delete database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
# Product category below
def product_category(request):
    return render(request,"pages/product_category.html")


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_product_category(request):
    if request.method == 'GET':
        product_categories = list(ProductCategory.objects.all().values('id', 'name_en','name_vi'))
        data = {
            "data": product_categories,
        }
        return JsonResponse(data, safe=False)


def is_valid_newproductcategory(product_category):
    exist_name_en = ProductCategory.objects.filter(name_en=product_category.name_en).exists()
    exist_name_vi = ProductCategory.objects.filter(name_vi=product_category.name_vi).exists()
    if exist_name_en:
        return False, "Danh mục đã tồn tại"
    if exist_name_vi:
        return False, "Danh mục đã tồn tại"
    if not product_category.name_en:
        return False, "Danh mục không được để trống"
    if not product_category.name_vi:
        return False, "Danh mục không được để trống"
    return True, None


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def create_product_category(request):
    if request.method == 'POST':
        product_category = json.loads(request.body)
        newProductCategory = ProductCategory(
            name_en=product_category['name_en'],
            name_vi=product_category['name_vi'],
        )
        check, msg = is_valid_newproductcategory(newProductCategory)
        if check:
            newProductCategory.save()

        data = {
            "success": check,
            "msg": msg
        }
        return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def update_product_category(request):
    if request.method == "POST":
        product_category = json.loads(request.body)
        product_category_in_db = ProductCategory.objects.get(id=product_category['id'])
        product_category_in_db.name_en=product_category['name_en']
        product_category_in_db.name_vi=product_category['name_vi']
        try:
            product_category_in_db.save()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as error:
            print(error)
            data = {
                "success": False,
                "msg": "Error when update database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def delete_product_category(request):
    if request.method == "POST":
        product_category = json.loads(request.body)
        try:
            u=ProductCategory.objects.filter(id = product_category['id']).delete()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as e:
            print(e)
            data = {
                "success": False,
                "msg": "Error when delete database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


# Article category below
@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def article_category(request):
    return render(request,"pages/article_category.html")


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_article_category(request):
    if request.method == 'GET':
        article_categories = list(ArticleCategory.objects.all().values('id', 'name_en','name_vi'))
        data = {
            "data": article_categories,
        }
        return JsonResponse(data, safe=False)


def is_valid_newarticlecategory(article_category):
    exist_name_en = ArticleCategory.objects.filter(name_en=article_category.name_en).exists()
    exist_name_vi = ArticleCategory.objects.filter(name_vi=article_category.name_vi).exists()
    if exist_name_en:
        return False, "Danh mục đã tồn tại"
    if exist_name_vi:
        return False, "Danh mục đã tồn tại"
    if not article_category.name_en:
        return False, "Danh mục không được để trống"
    if not article_category.name_vi:
        return False, "Danh mục không được để trống"
    return True, None


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def create_article_category(request):
    if request.method == 'POST':
        article_category = json.loads(request.body)
        newArticleCategory = ArticleCategory(
            name_en=article_category['name_en'],
            name_vi=article_category['name_vi'],
        )
        check, msg = is_valid_newarticlecategory(newArticleCategory)
        if check:
            newArticleCategory.save()
        data = {
            "success": check,
            "msg": msg
        }
        return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def update_article_category(request):
    if request.method == "POST":
        article_category = json.loads(request.body)
        article_category_in_db = ArticleCategory.objects.get(id=article_category['id'])
        article_category_in_db.name_en=article_category['name_en']
        article_category_in_db.name_vi=article_category['name_vi']
        try:
            article_category_in_db.save()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as error:
            print(error)
            data = {
                "success": False,
                "msg": "Error when update database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def delete_article_category(request):
    if request.method == "POST":
        article_category = json.loads(request.body)
        try:
            ArticleCategory.objects.filter(id = article_category['id']).delete()
            data = {
                "success": True,
                "msg": ""
            }
            return HttpResponse(json.dumps(data), content_type='text/json')
        except Exception as e:
            print(e)
            data = {
                "success": False,
                "msg": "Error when delete database"
            }
            return HttpResponse(json.dumps(data), content_type='text/json')


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def get_articles(request):
    values = ['id', 'articlelanguage__title', 'view', 'post_at']
    order_fields = ['-id']
    search_fields = ['articlelanguage__title']
    initial_query = Q(articlelanguage__language__code='vi')
    data = paginate(request.GET, Article, values, initial_query, search_fields, order_fields)
    return JsonResponse(data, safe=False)

@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
# Article below
def article_index (request):
    articles = Article.objects.all().order_by('-id')[:20]
    return render(request, 'pages/article/index.html', {"articles": articles})


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def article_store (request):
    form_vi = ArticleForm(prefix="vi")
    form_en = ArticleForm(prefix="en")
    article_category = ArticleCategory.objects.all()

    return render(request, 'pages/article/new.html', {
        "form_vi": form_vi,
        "form_en": form_en,
        "article_category": list(article_category)
    })


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def article_post_store (request):
    if request.method == "POST":
        data = json.loads(request.body)
        en_lang = Language.objects.filter(code='en').first()
        vi_lang = Language.objects.filter(code='vi').first()
        # Save media
        media = Media(file_path=data['thumbnail'])
        media.save()

        # Save article
        article = Article()
        article.post_at = datetime.strptime(data['post_at'], "%d/%m/%Y %H:%M:%S")
        article.article_category_id = data['article_category']
        article.view = 0
        article.thumbnail = media
        article.author = request.user
        article.save()
        # Save article language vi
        article_language = ArticleLanguage()
        article_language.title = data['title_vi']
        article_language.content = data['vi_content']
        article_language.language = vi_lang
        article_language.article = article
        article_language.save()
        # Save article language en
        article_language = ArticleLanguage()
        article_language.title = data['title_en']
        article_language.content = data['en_content']
        article_language.language = en_lang
        article_language.article = article
        article_language.save()
        return JsonResponse({
            "success": True,
            "message": ""
        })
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not supported"
        })

@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def uploads(request):
    if 'file[0]' in request.FILES:
        paths = []
        for file in request.FILES.values():
            file_name = f'{time.time()}.{file.name}'
            paths.append(os.path.join('uploads', file_name))
            default_storage.save(os.path.join(
                'uploads', file_name), ContentFile(file.read()))
        return JsonResponse({
            "success": True,
            "name": paths
        })
    else:
        file = request.FILES['file']
        file_name = f'{time.time()}.{file.name}'
        default_storage.save(os.path.join(
            'uploads', file_name), ContentFile(file.read()))
        return JsonResponse({
            "success": True,
            "name": os.path.join('uploads', file_name)
        })

@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def article_edit (request, id):
    article = Article.objects.filter(pk=id).first()
    if article is None:
        raise Http404("Article does not exist")
    if request.method == "GET":
        form_vi = ArticleForm(prefix="vi", instance=article.article_language_vi())
        form_en = ArticleForm(prefix="en", instance=article.article_language_en())
        article_category = ArticleCategory.objects.all()

        return render(request, 'pages/article/edit.html', {
            "article_category": list(article_category),
            "article": article,
            "form_vi": form_vi,
            "form_en": form_en,
        })
    if request.method == "DELETE":
        # Delete article
        try:
            article.thumbnail.delete();
            article.delete();
            return JsonResponse({
                "success": True,
                "data": id,
                "message": ""
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "Không xóa được bài viết"
            })


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def article_post_edit (request):
    if request.method == "POST":
        data = json.loads(request.body)
        en_lang = Language.objects.filter(code='en').first()
        vi_lang = Language.objects.filter(code='vi').first()
        article = Article.objects.filter(pk=data['id']).first()
        if article is None:
            raise Http404("Article does not exist")

        if article.thumbnail.file_path != data['thumbnail']:
            # Save media
            media = Media(file_path=data['thumbnail'])
            media.save()
            article.thumbnail = media
            # Remove oldfile
            # Path(os.path.join(settings.MEDIA_ROOT, article.thumbnail.file_path)).unlink()

        # Save article
        article.post_at = datetime.strptime(data['post_at'], "%d/%m/%Y %H:%M:%S")
        article.article_category_id = data['article_category']
        article.save()

        # Save article language vi
        article_language = ArticleLanguage.objects.filter(article_id=article.id, language_id=vi_lang.id).first()
        article_language.title = data['title_vi']
        article_language.content = data['vi_content']
        article_language.save()

        # Save article language en
        # Save article language vi
        article_language = ArticleLanguage.objects.filter(article_id=article.id, language_id=en_lang.id).first()
        article_language.title = data['title_en']
        article_language.content = data['en_content']
        article_language.save()

        return JsonResponse({
            "success": True,
            "message": ""
        })


# Product below
@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def get_products(request):
    values = ['id', 'view', 'des', 'productlanguage__name', 'is_hide_price']
    order_fields = ['-id']
    search_fields = ['productlanguage__name']
    initial_query = Q(productlanguage__language__code='vi')
    data = paginate(request.GET, Product, values, initial_query, search_fields, order_fields)

    # Get models
    for ele in data['data']:
        product = Product.objects.filter(id=ele['id']).first()
        models = ProductModel.objects.filter(product=product).values('weight', 'price', 'quantity')
        ele['models'] = list(models)

    return JsonResponse(data, safe=False)

@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def product_index(request):
    if not request.user.is_authenticated:
        user = authenticate(username='my_admin@svat.com', password='123')
        if user is not None:
            login(request, user)
    products = Product.objects.all().order_by('-id')[:20]
    return render(request, 'pages/product/index.html', {"products": products})


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def product_store(request):
    form_vi = ProductForm(prefix="vi")
    form_en = ProductForm(prefix="en")

    product_category = ProductCategory.objects.all()

    return render(request, 'pages/product/new.html', {
        "form_vi": form_vi,
        "form_en": form_en,
        "product_category": list(product_category)
    })


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def product_post_store(request):
    if request.method == "POST":
        data = json.loads(request.body)
        en_lang = Language.objects.filter(code='en').first()
        vi_lang = Language.objects.filter(code='vi').first()


        # Save product
        product = Product()
        product.product_category_id = data['product_category']
        product.view = 0
        product.is_hide_price = data['is_hide_price']
        product.save()

        for model in data.get('models', []):
            new_model = ProductModel(product=product, weight=model['weight'], price=model['price'], quantity=0)
            new_model.save()

        # Save media
        for image in data['images']:
            # Save product's images
            media = Media(file_path=image)
            media.save()
            product_image = ProductImage(media=media, product=product)
            product_image.save()

        # Save product language vi
        product_language = ProductLanguage()
        product_language.name = data['name_vi']
        product_language.des = data['vi_des']
        product_language.language = vi_lang
        product_language.product = product
        product_language.save()

        # Save product language en
        product_language = ProductLanguage()
        product_language.name = data['name_en']
        product_language.des = data['en_des']
        product_language.language = en_lang
        product_language.product = product
        product_language.save()
        return JsonResponse({
            "success": True,
            "message": ""
        })
    else:
        return JsonResponse({
            "success": False,
            "message": "Method not supported"
        })


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def product_edit(request, id):
    product = Product.objects.filter(pk=id).first()
    if product is None:
        raise Http404("Product does not exist")
    if request.method == "GET":
        form_vi = ProductForm(
            prefix="vi", instance=product.product_language_vi())
        form_en = ProductForm(
            prefix="en", instance=product.product_language_en())
        product_category = ProductCategory.objects.all()
        product_images = ProductImage.objects.filter(product=product).all()
        images = []
        for ele in product_images:
            image = Media.objects.filter(id=ele.media_id).first()
            images.append(image)

        product_models = ProductModel.objects.filter(product=product).values('weight', 'price')

        return render(request, 'pages/product/edit.html', {
            "product_category": list(product_category),
            "product": product,
            "product_images": json.dumps(images, default=lambda x: x.__dict__['file_path']),
            "form_vi": form_vi,
            "form_en": form_en,
            "product_models": list(product_models)
        })
    if request.method == "DELETE":
        # Delete product
        try:
            product_models = ProductModel.objects.filter(product=product)
            product_models.delete()
            product_images = ProductImage.objects.filter(product=product)
            product_images.delete()
            product.delete()
            return JsonResponse({
                "success": True,
                "data": id,
                "message": ""
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "Không xóa được sản phẩm"
            })


@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
@transaction.atomic
def product_post_edit(request):
    if request.method == "POST":
        data = json.loads(request.body)
        en_lang = Language.objects.filter(code='en').first()
        vi_lang = Language.objects.filter(code='vi').first()
        product = Product.objects.filter(pk=data['id']).first()
        product_images = ProductImage.objects.filter(product=product).all()
        models = data.get('models', [])

        if product is None:
            raise Http404("Product does not exist")

        for image in product_images:
            # Remove old product's images
            if image.media.file_path not in data['images']:
                Path(os.path.join(settings.MEDIA_ROOT, image.media.file_path)).unlink()
                image.delete()
            else:
                data['images'].remove(image.media.file_path)


        for image in data['images']:
            # Save product's images
            media = Media(file_path=image)
            media.save()
            product_image = ProductImage(media=media, product=product)
            product_image.save()


        ProductModel.objects.filter(product=product).delete()
        for model in models:
            new_model = ProductModel(product=product, weight=model['weight'], price=model['price'])
            new_model.save()
        # Save product
        product.product_category_id = data['product_category']
        product.is_hide_price = data['is_hide_price']
        product.save()

        # Save product language vi
        product_language = ProductLanguage.objects.filter(
            product_id=product.id, language_id=vi_lang.id).first()
        product_language.name = data['name_vi']
        product_language.des = data['vi_des']
        product_language.save()

        # Save product language en
        # Save product language vi
        product_language = ProductLanguage.objects.filter(
            product_id=product.id, language_id=en_lang.id).first()
        product_language.name = data['name_en']
        product_language.content = data['en_des']
        product_language.save()

        return JsonResponse({
            "success": True,
            "message": ""
        })


# Order below
@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def order_index(request):
    if not request.user.is_authenticated:
        user = authenticate(username='my_admin@svat.com', password='123')
        if user is not None:
            login(request, user)
    return render(request, 'pages/orders.html')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def update_order(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body)
            order_id = req_data['id']
            status = int(req_data['status'])
            order = Order.objects.filter(pk=order_id).first()

            # Neu huy => return lai quantity
            if status == 4:
                order_products = order.order_product()
                for order_product in order_products :
                    product_model = order_product.product_model
                    product_model.quantity += order_product.quantity
                    product_model.save()

            order.status = status
            order.save()

            data = {
                "success": True,
                "msg": "",
                "data": {}
            }
            return JsonResponse(data, safe=False)
        except Exception:
            data = {
                "success": False,
                "msg": "Xảy ra lỗi khi cập nhật order!",
                "data": {}
            }
            return JsonResponse(data, safe=False)


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_order(request):
    if request.method == 'GET':
        values = ['id', 'name', 'address', 'phone_number', 'created', 'status']
        order_fields = ['status', '-id']
        search_fields = ['email', 'name', 'address', 'phone_number']
        data = paginate(request.GET, Order, values, search_fields=search_fields, order_fields=order_fields)
        return JsonResponse(data, safe=False)


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_detail_order(request):
    if request.method == 'POST':
        order_id = json.loads(request.body)['id']
        order = Order.objects.filter(pk=order_id).values('id', 'name', 'address', 'email', 'phone_number', 'shipping_fee', 'total', 'total_products', 'status').first()
        detail_orders = list(OrderProduct.objects.filter(order=order_id).values('id', 'quantity', 'product_model').all())
        data = {
            "order": order,
            "detail_orders": []
        }

        for ele in detail_orders:
            product_model = ProductModel.objects.filter(pk=ele['product_model']).first()
            product = Product.objects.filter(pk=product_model.product.id).first()

            data['detail_orders'].append({
                "id": product.id,
                "quantity": ele['quantity'],
                "name": product.product_language_vi().name,
                "cost": product_model.price
            })

        return JsonResponse(data, safe=False)


#Import Order
@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def import_order(request):
    products = list(Product.objects.all().values('id'))
    return render(request,"pages/import_order.html",{"len":len(products)})


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_import_order(request):
    if request.method == 'GET':
        import_orders = list(ImportOrder.objects.all().values('id', 'created','user'))
        for i in range(0,len(import_orders)):
            user_mail=User.objects.get(id=import_orders[i]['user']).email
            id=import_orders[i]['user']=user_mail
        data = {
            "data": import_orders,
        }
        return JsonResponse(data, safe=False)


# Order below
@user_passes_test(PERMISSIONS.admin_congtacvienvietbai, login_url='admin.403')
def order_index(request):
    if not request.user.is_authenticated:
        user = authenticate(username='my_admin@svat.com', password='123')
        if user is not None:
            login(request, user)
    return render(request, 'pages/orders.html')


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def view_detail(request):
    if request.method == "POST":
        req = json.loads(request.body)
        import_order_products = ImportOrder.objects.filter(pk=req['id']).first().importorderproduct_set.values('quantity', 'id', 'product_model').all()
        info = ImportOrder.objects.values('id', 'created').get(pk=req['id'])

        result = []
        for import_product in import_order_products:
            product_model = ProductModel.objects.values('product', 'weight', 'price').get(pk=import_product['product_model'])
            product = Product.objects.get(pk=product_model['product'])
            tmp = {
                'quantity': import_product['quantity'],
                'weight': product_model['weight'],
                'price': product_model['price'],
                'name': f'#{product.id} - {product.product_language_vi().name}' 
            }
            result.append(tmp)

        data={
            'data': result,
            'info': info,
            'success':True
        }
        return JsonResponse(data)

@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def store_import_order(request):
    if request.method == "POST":
        result = {
            "success": True,
            "message": ""
        }
        data = json.loads(request.body)
        if len(data) <= 0:
            return JsonResponse(result)

        # import order
        newImportOrder=ImportOrder(created=datetime.now(), user=request.user)
        newImportOrder.save()

        for item in data:
            # Update quantity
            product_model = ProductModel.objects.get(pk=int(item['product_model']))
            product_model.quantity = int(product_model.quantity) + int(item['quantity'])
            product_model.save()

            # import product
            import_order_product = ImportOrderProduct(quantity=item['quantity'], import_order=newImportOrder, product_model=product_model)
            import_order_product.save()

        return JsonResponse(result)
    return JsonResponse({
        "success": False,
        "message": "Lỗi bất ngờ"
    })

@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_product(request):
    if request.method == "GET":
        products = Product.objects.all()
        result = []
        for product in products:
            tmp = {
                'id': product.pk,
                'text': f"#{product.pk} - {product.product_language_vi().name}",
                'models': json.dumps(list(product.product_model.values('id', 'weight', 'quantity').all()), cls=DjangoJSONEncoder)
            }
            result.append(tmp)

        data = {
            "results": result,
        }
        return JsonResponse(data, safe=False)

# Message
@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def message(request):
    return render(request, 'pages/message.html')

@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def get_all_message(request):
    if request.method == 'GET':
        values = ['id', 'name', 'email', 'message', 'created', 'status']
        order_fields = ['-created']
        search_fields = ['name', 'email', 'message']
        data = paginate(request.GET, Message, values, search_fields=search_fields, order_fields=order_fields)
        return JsonResponse(data, safe=False)


@user_passes_test(PERMISSIONS.admin_quanly, login_url='admin.403')
def process_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id_message=int(data['id'])
        message=Message.objects.get(id=id_message)
        message.status=1
        message.save()
        data={
            "success":True,
        }
        return JsonResponse({
            "success": True,
        })


def get_message_in_progress(request):
    if request.user.is_authenticated and (request.user.role == 12 or request.user.role == 10):
        messages = Message.objects.filter(status=0)
        print(len(messages))
        return JsonResponse({
            'success': True,
            'total': len(messages)
        })
    else:
        return JsonResponse({
            'success': False,
            'total': 0
        }) 


def get_order_in_progress (request):
    if request.user.is_authenticated and (request.user.role == 12 or request.user.role == 10):
        orders = Order.objects.filter(status__in=[0,1,2])
        return JsonResponse({
            'success': True,
            'total': len(orders)
        })
    else:
        return JsonResponse({
            'success': False,
            'total': 0
        })


def send_email_order_in_progress (request):
    if request.method == "POST":
        data = json.loads(request.body)
        order_id = data['order_id']
        order = Order.objects.filter(pk=order_id).first()
        order.shipping_fee = data['shipping_fee']
        order.total = int(order.total_products) + int(data['shipping_fee'])
        order.save()
        
        subject = '[SVAT] Xác nhận đơn hàng'
        msg_html = render_to_string('user/pages/checkout/checkout-email-form.html', { 'order': order })
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [order.email]
        send_mail(subject, msg_html, email_from, recipient_list, html_message=msg_html)
        return JsonResponse({
            'success': True
        })
