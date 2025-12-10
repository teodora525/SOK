"""
URL Configuration za graph_explorer
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('explorer.urls')),
]