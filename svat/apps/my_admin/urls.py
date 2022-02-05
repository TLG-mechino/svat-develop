from django.urls import path

from . import views

urlpatterns = [
    # Dashboard
    path('dashboard', views.index, name='admin.dashboard'),
    path('login', views.handle_login, name='admin.login'),
    path('logout', views.handle_logout, name='admin.logout'),
    path('403', views.handle403, name='admin.403'),


    # User
    path('user', views.user, name='admin.user'),
    path('getAllUser', views.get_all_user, name='admin.get_all_user'),
    path('createUser', views.create_user, name='admin.create_user'),
    path('updateUser', views.update_user, name='admin.update_user'),
    path('deleteUser', views.delete_user, name='admin.delete_user'),

    # Product category
    path('product_category', views.product_category, name='admin.product_category'),
    path('getAllProductCategory', views.get_all_product_category, name='admin.get_all_product_category'),
    path('createProductCategory', views.create_product_category, name='admin.create_product_category'),
    path('updateProductCategory', views.update_product_category, name='admin.update_product_category'),
    path('deleteProductCategory', views.delete_product_category, name='admin.delete_product_category'),

    # Article
    path('getArticles', views.get_articles, name='admin.get.article'),
    path('article', views.article_index, name='admin.article'),
    path('article/<int:id>', views.article_edit, name='admin.article.get.edit'),
    path('article/edit', views.article_post_edit, name='admin.article.post.edit'),
    path('article/new', views.article_store, name='admin.article.get.store'),
    path('article/store', views.article_post_store, name='admin.article.post.store'),
    path('uploads', views.uploads, name='admin.upload'),

    # Product
    path('getProducts', views.get_products, name='admin.get.product'),
    path('product', views.product_index, name='admin.product'),
    path('product/<int:id>', views.product_edit, name='admin.product.get.edit'),
    path('product/new', views.product_store, name='admin.product.get.store'),
    path('product/edit', views.product_post_edit, name='admin.product.post.edit'),
    path('product/store', views.product_post_store, name='admin.product.post.store'),

    #Article Category
    path('article_category', views.article_category, name='admin.article_category'),
    path('getAllArticleCategory', views.get_all_article_category, name='admin.get_all_article_category'),
    path('createArticleCategory', views.create_article_category, name='admin.create_article_category'),
    path('updateArticleCategory', views.update_article_category, name='admin.update_article_category'),
    path('deleteArticleCategory', views.delete_article_category, name='admin.delete_article_category'),

    # Order
    path('order', views.order_index, name='admin.order'),
    path('getAllOrder', views.get_all_order, name='admin.get_all_order'),
    path('updateOrder', views.update_order, name='admin.update_order'),
    path('getDetailOrder', views.get_detail_order, name='admin.get_detail_order'),
    path('getOrderInProgress', views.get_order_in_progress, name='admin.get_order_in_progress'),
    path('sendEmailOrderInProgress', views.send_email_order_in_progress, name='admin.send_email_order_in_progress'),

    #Import Order
    path('GetAllImportOrder', views.get_all_import_order, name='admin.get_all_import_order'),
    path('ImportOrder', views.import_order, name='admin.import_order'),
    path('ViewDetail', views.view_detail, name='admin.view_detail'),   
    path('storeImportOrder', views.store_import_order, name='import_order.post'),
    path('GetAllProduct', views.get_all_product, name='admin.get_all_product'),

    # Order
    path('order', views.order_index, name='admin.order'),
    path('getAllOrder', views.get_all_order, name='admin.get_all_order'),
    path('updateOrder', views.update_order, name='admin.update_order'),
    path('getDetailOrder', views.get_detail_order, name='admin.get_detail_order'),


    #Message
    path('message', views.message, name='admin.message'),
    path('get_all_message', views.get_all_message, name='admin.get_all_message'),
    path('process_message', views.process_message, name='admin.process_message'),
    path('getMessageInProgress', views.get_message_in_progress, name='admin.get_message_in_progress'),

]
