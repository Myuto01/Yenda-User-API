from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token



urlpatterns = [
    path("user_registeration/", views.RegistrationAPIView.as_view(), name="user_registeration" ),
    path("api/v1/auth/login", views.UserLogin.as_view(), name="user_login" ),
    path("user/<int:pk>/update/", views. UserUpdateView.as_view(), name="update_details" ),
    path("user/<int:pk>/change_password/", views.PasswordChangeView.as_view(), name="change_password"),
    path('auth/', obtain_auth_token, name='auth'),

    #comment out in production
    path('login/',views.login , name='login'),
    path('dashboard/', views.dashboard, name = 'dashboard')

]