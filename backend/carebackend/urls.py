"""carebackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from places.views import (
    neighborhood_detail,
    place_detail,
    submit_email_for_place,
    submit_gift_card_link,
    submit_new_place
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/places/detail', place_detail),
    path('api/places/by_neighborhood', neighborhood_detail),
    path('api/places/submit_email', submit_email_for_place),
    path('api/places/submit_gift_card_link', submit_gift_card_link),
    path('api/places/submit_new_place', submit_new_place)
]
