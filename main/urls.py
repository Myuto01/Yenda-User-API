from django.urls import path
from . import views


urlpatterns = [
    path("user_registeration/", views.RegistrationAPIView.as_view(), name="user_registeration" ),
    path("user_login/", views.UserLogin.as_view(), name="user_login" ),
    path("user/<int:pk>/update/", views. UserUpdateView.as_view(), name="update_details" ),
    path("user/<int:pk>/change_password/", views.PasswordChangeView.as_view(), name="change_password"),
]