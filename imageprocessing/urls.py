"""
URL configuration for imageprocessing project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from .views.he import HistogramEqualizationView
from .views.dhe import DynamicHistogramEqualizationView
from .views.ying import ImageProcessingView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('histogram-equalization/', HistogramEqualizationView.as_view(), name='histogram_equalization'),  # Add the new URL pattern]
    path('dynamic_histogram_equalization/', DynamicHistogramEqualizationView.as_view(), name='dynamic_histogram_equalization'),
    path('fusion-framework/', ImageProcessingView.as_view(), name='process_image')
]