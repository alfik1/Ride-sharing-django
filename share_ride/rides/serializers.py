from rest_framework import serializers
from .models import Ride


class RideSerializer(serializers.ModelSerializer):
    rider_username = serializers.CharField(source='rider.username', read_only=True)

    class Meta:
        model = Ride
        fields = ['id', 'rider', 'rider_username', 'pickup_location', 'dropoff_location', 'status', 'created_at']
        read_only_fields = ['id', 'rider', 'status', 'created_at']


class RideStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ['status']
        extra_kwargs = {
            'status': {'required': True}
        }


class RideAcceptSerializer(serializers.Serializer):
    ride_id = serializers.IntegerField()


class RideLocationUpdateSerializer(serializers.Serializer):
    current_latitude = serializers.FloatField(required=True)
    current_longitude = serializers.FloatField(required=True)