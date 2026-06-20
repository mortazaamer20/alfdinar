from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how/', views.how, name='how'),
    path('visits/', views.visits, name='visits'),
    path('cases/', views.cases, name='cases'),
    path('contact/', views.contact, name='contact'),
]
