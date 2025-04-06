from django.urls import path
from .views import *


urlpatterns = [
    path('profile-signup', RegisterView.as_view(), name="profile_signup" ),
    path('signin', Signin.as_view(), name='signin'),
    path('update-driver-location/', UpdateDriverLocationView.as_view(), name='update-driver-location')
]