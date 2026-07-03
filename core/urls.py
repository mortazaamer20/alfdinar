from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how/', views.how, name='how'),
    path('visits/', views.visits, name='visits'),
    path('visits/<int:pk>/', views.visit_detail, name='visit_detail'),
    path('cases/', views.cases, name='cases'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),
    path('contact/', views.contact, name='contact'),
]
