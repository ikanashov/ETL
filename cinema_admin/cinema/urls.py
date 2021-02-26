from django.urls import include, path


urlpatterns = [
    path('api/', include('cinema.api.urls')),
]
