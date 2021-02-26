from cinema.api.v1 import views

from django.urls import path

urlpatterns = [
    path('movies/', views.Movies.as_view()),
    path('movies/<uuid:pk>/', views.Movies.as_view()),
]
