"""
URL configuration for Store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from core.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name='home'),
    path('api/send_purchase_request/', send_purchase_request, name='send_purchase_request'),
    path("Shop_1/", shop_1, name='shop'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),

    # Manager URLs
    path('manager/', manager_view, name='manager'),
    path('manager/accept/<int:request_id>/', accept_request, name='accept_request'),
    path('manager/reject/<int:request_id>/', reject_request, name='reject_request'),

    # New URLs for product to make workflow
    path('manager/product_finished/<int:product_to_make_id>/', product_finished, name='product_finished'),
    path('manager/product_picked_up/<int:product_to_make_id>/', product_picked_up, name='product_picked_up'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)