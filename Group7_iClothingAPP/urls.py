"""Group7_iClothingAPP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', views.Homepage),
    path(r'Login/', views.login),
	path(r'Aboutcmpy/', views.abt_cmpy),
	path(r'cart_Login/', views.login),
	path(r'reload_hmpg/', views.rld_hmpg),
	path("Register/", views.register, name="register"),
	path("User/", views.login_request, name="login"),
	path("retrieve_cred/", views.retrieve_cred),
	path("Logout/", views.logout_request, name="logout"),
	path("Address/", views.saved_Address),
	path("add_address/", views.add_Address),
	path("reload_hmpg_aft_login/", views.rld_hmpg_after_login),
	path("approve_reject/", views.approve_reject),
	path("upld_new/", views.upld_new),
	path("upload_file/", views.upload_file),
	path("open_cart/", views.open_cart),
	path("update_addrs/", views.update_addrs),
	path("save_cart_checkout/", views.save_cart_checkout),
	path("pay_page/", views.pay_page),
	path("del_ord_email/", views.del_ord_email),
	path("prod_catalog/", views.prod_catalog),
	path("prod_cat/", views.prod_cat),
]

#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
