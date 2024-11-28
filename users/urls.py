from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.landing, name='landing'),  # Landing page
    path('register/', views.register, name='register'),  # Registration page
    path('kini/', views.kini, name='kini'),  # kini page
    path('logout/', views.logout, name='logout'),
    path('login/', views.login_user, name='login'),  # Login page
    path('home/', views.home, name='home'),  # Home page
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Product detail page
    path('product/<int:product_id>/review/', views.product_review, name='product_review'),  # Product review page
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),  # Buy now page
    path('save-session-data/', views.save_session_data, name='save_session_data'),
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('become-distributor/', views.become_distributor, name='become_distributor'),  # Become a distributor page
    path('buy-as-distributor/<int:product_id>/', views.buy_as_distributor, name='buy_as_distributor'),
    path('distributor-checkout/', views.distributor_checkout, name='distributor_checkout'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),  # distributor checkout page
    path('success/', views.success_page, name='success_page'),  # distributor checkout page
    path('customer_orders/', views.customer_orders, name='customer_orders'),  # distributor checkout page
    path('home/men-perfume/', views.men, name='men'),  # men perfume page
    path('home/women-perfume/', views.women, name='women'),  # women perfume page
    path('create-article/', views.create_article, name='create_article'),  # Create Article page
    path('article/delete/<int:post_id>/', views.delete_article, name='delete_article'),
    path('articles/edit/<int:article_id>/', views.edit_article, name='edit_article'),
    path('articles/', views.articles, name='articles'),  # Articles list page
    path('article/<str:title>', views.article_details, name='article_details'),  # Article details page
    path('faq/', views.faq, name='faq'),  # FAQ page
    path('contact-us/', views.contact_us, name='contact_us'),  # Contact us page
    path('contact-us_messages/', views.contact_us_messages, name='contact_us_messages'),  # Messages from Contact us page
    path('reviews/', views.reviews, name='reviews'),  # Reviews page

    path('dashboard/user-activity/', views.user_activity, name='user_activity'),
    path('dashboard/view-users/', views.view_users, name='view_users'),

    path('dashboard/user/<int:user_id>/', views.user_detail, name='user_detail'),
    # Dashboard page
    path('dashboard/', views.dashboard, name='dashboard'),

    # Pending Orders page
    path("dashboard/pending-orders/", views.pending_orders, name="pending_orders"),
    path("dashboard/pending-orders/<str:location>/", views.orders_by_location, name="orders_by_location"),

    # Confirmed Orders page
    # path("dashboard/confirmed-orders/", views.confirmed_orders, name="confirmed_orders"),
    path('dashboard/confirmed-orders/<str:location>/', views.confirmed_orders_by_location, name='confirmed_orders_by_location'),
    path('confirm-order/<int:order_id>/', views.confirm_order, name='confirm_order'),

    path('product/add-for-men/', views.add_for_men, name='add_for_men'),
    path('product/add-for-women/', views.add_for_women, name='add_for_women'),
    path('dashboard/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('dashboard/product/<int:product_id>/', views.product_detail_back, name='product_detail_back'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/men-list/', views.men_list, name='men_list'),
    path('product/women-list/', views.women_list, name='women_list'),

    # Order Detail page for pending orders (by location)
    path('dashboard/order/<int:order_id>/', views.order_details, name='order_details'),

    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),


    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/delete-account/', views.delete_account, name='delete_account'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
