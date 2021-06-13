"""iCrawler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.conf import settings
from django.conf.urls import url,static
from django.views.generic import TemplateView
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.scraper_view ),
    url(r'^api/crawl/', views.crawl, name='crawl'),
    url(r'^csv/', views.csv_export, name='csv_export'),
    url(r'^get_csv_filename/', views.get_csv_filename, name='get_csv_filename'),
    url(r'^scraper_date/', views.get_scraper_date, name='get_scraper_date'),
]

# This is required for static files while in development mode. (DEBUG=TRUE)
# No, not relevant to scrapy or crawling :)
if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
