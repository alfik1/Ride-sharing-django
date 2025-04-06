from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from accounts.models import Profile
from rides.models import Ride
from rest_framework.exceptions import ValidationError
from django.urls import reverse

class ModelTests(TestCase):
    def setUp(self):
        # Create test users and profiles
        self.user_rider = User.objects.create_user(username='rider', password='password')
        self.profile_rider = Profile.objects.create(
            user=self.user_rider,
            first_name='Rider',
            last_name='One',
            email='rider@example.com',
            user_type='rider'
        )
        
        self.user_driver = User.objects.create_user(username='driver', password='password')
        self.profile_driver = Profile.objects.create(
            user=self.user_driver,
            first_name='Driver',
            last_name='One',
            email='driver@example.com',
            user_type='driver'
        )
        
    ### Profile Model Tests ###
    def test_profile_creation(self):
        """Test that a Profile can be created with all fields."""
        self.assertEqual(self.profile_rider.first_name, 'Rider')
        self.assertEqual(self.profile_rider.last_name, 'One')
        self.assertEqual(self.profile_rider.email, 'rider@example.com')
        self.assertEqual(self.profile_rider.user_type, 'rider')
        self.assertTrue(self.profile_rider.is_active)

    def test_profile_str(self):
        """Test the __str__ method of Profile."""
        self.assertEqual(str(self.profile_rider), 'Rider')

    def test_profile_full_name(self):
        """Test the full_name property of Profile."""
        self.assertEqual(self.profile_rider.full_name, 'Rider One')

    def test_active_manager(self):
        """Test that ActiveManager only returns active and non-deleted profiles."""
        # Create an inactive profile
        inactive_profile = Profile.objects.create(
            user=User.objects.create_user('inactive', 'password'),
            first_name='Inactive',
            is_active=False
        )
        # Create a deleted profile
        deleted_profile = Profile.objects.create(
            user=User.objects.create_user('deleted', 'password'),
            first_name='Deleted',
            deleted=True
        )
        profiles = Profile.objects.all()
        self.assertIn(self.profile_rider, profiles)
        self.assertNotIn(inactive_profile, profiles)
        self.assertNotIn(deleted_profile, profiles)

class APITests(TestCase):
    def setUp(self):
        # Create test users and profiles
        self.user_rider = User.objects.create_user(username='rider', password='password')
        self.profile_rider = Profile.objects.create(
            user=self.user_rider,
            first_name='Rider',
            last_name='One',
            email='rider@example.com',
            user_type='rider'
        )
        
        self.user_driver = User.objects.create_user(username='driver', password='password')
        self.profile_driver = Profile.objects.create(
            user=self.user_driver,
            first_name='Driver',
            last_name='One',
            email='driver@example.com',
            user_type='driver'
        )
        
        # Create a ride
        self.ride = Ride.objects.create(
            rider=self.profile_rider,
            pickup_location='Pickup',
            dropoff_location='Dropoff',
            status='requested'
        )
        
        self.client = APIClient()