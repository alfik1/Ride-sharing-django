from django.shortcuts import render
from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from helpers.common import success_response, error_response, get_user_profile
from rest_framework import status
from django.contrib.auth import login, authenticate
from .serializers import RegisterSerializer
#user registration view

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return success_response(success_message="profile has been created", status=status.HTTP_201_CREATED)


class Signin(APIView):
    """User Authentication."""

    def post(self, request):
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')
            user = authenticate(username=username, password=password)
            if user is None or (user and not user.is_active):
                return error_response(error_message='Invalid credentials. Please try again.', errors={'user': ['Invalid credentials']}, status=status.HTTP_400_BAD_REQUEST)
    
            profile = get_user_profile(user.id)
            if not profile:
                return error_response(errors={'username': ['There is no existing user profile.']}, status=status.HTTP_400_BAD_REQUEST)
            login(request, user)
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            return success_response({'access': str(access_token),'refresh': str(refresh)},
                                        status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return error_response(error_message="Something went wrong!", exception_info = str(e))


class UpdateDriverLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.profile.user_type != "driver":
            return error_response(
                error_message="Only drivers can update their location.",
                status=status.HTTP_403_FORBIDDEN
            )

        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if latitude is None or longitude is None:
            return error_response(
                error_message="Latitude and longitude are required.",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = request.user.profile
            profile.current_latitude = float(latitude)
            profile.current_longitude = float(longitude)
            profile.save()
            return success_response(
                success_message="Location updated successfully.",
                data={"latitude": latitude, "longitude": longitude}
            )
        except Exception as e:
            return error_response(
                error_message="Something went wrong!",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )