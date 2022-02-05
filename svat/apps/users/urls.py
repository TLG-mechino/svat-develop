from django.urls import path 
from . import views

urlpatterns = [
    # Top-page
    path('', views.index, name='user.index'),

    # Register
    path('register', views.handle_register, name='user.register'),
    path('register/verify/<str:email>/<str:verify_token>', views.verify_email, name='user.verify_email'),
    path('register/success', views.success_register, name='user.success_register'),
    path('register/re-send-activate', views.resend_activate, name='user.resend_activate'),

    # Login
    path('login', views.handle_login, name='user.login'),
    path('logout', views.handle_logout, name='user.logout'),

    # Forget password
    path('forget-password', views.forget_password, name='user.forget-password'),
    path('forget-password/send-mail', views.forget_password_send_mail, name='user.forget-password-send-mail'),
    path('forget-password/check-secret-token', views.forget_password_check_secret_token, name='user.forget-password-check-secret-token'),
    path('forget-password/change-password', views.forget_password_change_password, name='user.forget-password-change-password'),

    path('product/<int:id>', views.detail_product, name='user.detail_product'),
   
    # Product List
    path('categories', views.get_product_categories, name='user.product_categories'),
    path('product', views.get_product_list, name='user.product.list'),

    # Profile
    path('user/profile', views.view_profile, name='user.view_profile'),
    path('user/updateprofile', views.update_profile, name='user.update_profile'),


    # Articles list
    path('articles', views.get_article_list, name='user.article.list'),

    #Orders
    path('user/orders', views.view_orders, name='user.view_orders'),
    path('user/deleteOrder', views.delete_orders, name='user.delete_orders'),

    # Shopping cart
    path('shopping-cart', views.shopping_cart, name='user.shopping_cart'),
    path('get-shopping-cart', views.get_shopping_cart, name='user.get_shopping_cart'),
    path('add-product-to-cart', views.add_product_to_cart, name='user.add_product_to_cart'),
    path('update-product-to-cart', views.update_product_to_cart, name='user.update_product_to_cart'),
    path('delete-product-to-cart', views.delete_product_to_cart, name='user.delete_product_to_cart'),
    path('checkout-now', views.checkout_now, name='user.checkout_now'),

    # Contact
    path('contact', views.contact, name='user.contact'),
    path('send_message', views.send_message, name='user.send_message'),


    path('checkout', views.checkout, name='user.checkout'),
    
    path('article/<int:id>', views.detail_article, name='user.detail_article'),
]
