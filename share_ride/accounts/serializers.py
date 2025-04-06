from accounts.models import Profile
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password



class RegisterSerializer(serializers.ModelSerializer):
    # Input fields (write-only)
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(write_only=True, required=True)
    user_type = serializers.CharField(write_only=True, required=True)  # now consistent naming

    # Output fields (read-only)
    profile_user_type = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username', 'password', 'email',
            'first_name', 'last_name', 'user_type',  
            'profile_user_type', 'full_name'        
        )
        extra_kwargs = {
            'username': {'write_only': True},
        }

    def get_profile_user_type(self, obj):
        return getattr(obj.profile, 'user_type', None)

    def get_full_name(self, obj):
        return f"{obj.profile.first_name} {obj.profile.last_name}".strip() if hasattr(obj, 'profile') else ''

    def create(self, validated_data):
        # Extract user & profile-related fields
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email')
        user_type = validated_data.pop('user_type')

        # Create the user
        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(validated_data['password']),
        )

        # Create the linked profile
        Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_type=user_type,
        )

        return user

class ProfileSerializerFields(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ["id","first_name","last_name","email","full_name"]

    def get_full_name(self,obj):
        return obj.full_name()