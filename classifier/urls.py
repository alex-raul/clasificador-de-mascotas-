from django.urls import path
from . import views

app_name = 'classifier'

urlpatterns = [
    path('', views.home, name='home'),
    path('classifier/', views.classifier_view, name='classifier'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('calculator/', views.calculator_view, name='calculator'),
]