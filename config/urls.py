from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.LoginPageView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('r/<str:token>/', views.review_landing, name='review_landing'),
    path('', include('core.urls')),
]
