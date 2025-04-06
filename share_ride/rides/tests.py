from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from accounts.models import Profile
from rides.models import Ride
from rest_framework.exceptions import ValidationError
from django.urls import reverse
import json

class ModelTests(TestCase):
    def setUp(self):
        self.user_rider = User.objects.create_user(username='rider', password='password')
        self.profile_rider = Profile.objects.create(
            user=self.user_rider,
            first_name='Rider',
            last_name='One',
            email='rider@example.com',
            user_type='rider'
        )
        self.ride = Ride.objects.create(
            rider=self.profile_rider,
            pickup_location='Pickup',
            dropoff_location='Dropoff',
            status='requested'
        )

    def test_ride_creation(self):
        self.assertEqual(self.ride.rider, self.profile_rider)
        self.assertIsNone(self.ride.driver)
        self.assertEqual(self.ride.pickup_location, 'Pickup')
        self.assertEqual(self.ride.dropoff_location, 'Dropoff')
        self.assertEqual(self.ride.status, 'requested')

    def test_ride_str(self):
        self.assertEqual(str(self.ride), f"Ride {self.ride.id} - Rider One to Dropoff")

    def test_ride_status_choices(self):
        ride = Ride(
            rider=self.profile_rider,
            pickup_location='A',
            dropoff_location='B',
            status='invalid'
        )
        with self.assertRaises(ValidationError) as context:
            ride.full_clean()
        
        self.assertIn('status', context.exception.message_dict)

class APITests(TestCase):
    def setUp(self):
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
        self.ride = Ride.objects.create(
            rider=self.profile_rider,
            pickup_location='Pickup',
            dropoff_location='Dropoff',
            status='requested'
        )
        self.client = APIClient()

    def test_ride_create_as_rider(self):
        self.client.force_authenticate(user=self.user_rider)
        data = {'pickup_location': 'New Pickup', 'dropoff_location': 'New Dropoff'}
        response = self.client.post(reverse('ride-create'), data)
        self.assertEqual(response.status_code, 201)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(Ride.objects.count(), 2)

    def test_ride_create_as_driver(self):
        self.client.force_authenticate(user=self.user_driver)
        data = {'pickup_location': 'New Pickup', 'dropoff_location': 'New Dropoff'}
        response = self.client.post(reverse('ride-create'), data)
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['detail'], 'Drivers are not allowed to request rides.')

    def test_ride_detail(self):
        self.client.force_authenticate(user=self.user_rider)
        response = self.client.get(reverse('ride-detail', args=[self.ride.id]))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['id'], self.ride.id)
        self.assertEqual(response_data['rider'], self.profile_rider.id)

    def test_ride_detail_not_found(self):
        self.client.force_authenticate(user=self.user_rider)
        response = self.client.get(reverse('ride-detail', args=[999]))
        self.assertEqual(response.status_code, 500) 
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['detail'], 'Ride not found')

    def test_ride_list(self):
        self.client.force_authenticate(user=self.user_rider)
        response = self.client.get(reverse('ride-list'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response_data), 1)

    def test_driver_view_available_rides(self):
        self.client.force_authenticate(user=self.user_driver)
        response = self.client.get(reverse('driver-accept-ride'))
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn('results', response_data)
        self.assertIn('data', response_data['results'])
        self.assertEqual(len(response_data['results']['data']), 1)

    def test_driver_accept_ride(self):
        self.client.force_authenticate(user=self.user_driver)
        data = {'ride_id': self.ride.id}
        response = self.client.post(reverse('driver-accept-ride'), data)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['message'], 'Ride accepted successfully.')
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.driver, self.profile_driver)

    def test_driver_cannot_accept_multiple_rides(self):
        Ride.objects.create(
            rider=self.profile_rider,
            driver=self.profile_driver,
            pickup_location='A',
            dropoff_location='B',
            status='accepted'
        )
        self.client.force_authenticate(user=self.user_driver)
        data = {'ride_id': self.ride.id}
        response = self.client.post(reverse('driver-accept-ride'), data)
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['message'], 'You are already assigned to an active ride.')

    def test_update_ride_status_as_assigned_driver(self):
        self.ride.driver = self.profile_driver
        self.ride.status = 'accepted'
        self.ride.save()
        self.client.force_authenticate(user=self.user_driver)
        data = {'status': 'started'}
        response = self.client.patch(reverse('ride-update-status', args=[self.ride.id]), data)
        self.assertEqual(response.status_code, 200)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'started')

    def test_update_ride_status_as_non_assigned_driver(self):
        another_driver = User.objects.create_user(username='driver2', password='password')
        Profile.objects.create(user=another_driver, first_name='Driver2', user_type='driver')
        self.client.force_authenticate(user=another_driver)
        data = {'status': 'started'}
        response = self.client.patch(reverse('ride-update-status', args=[self.ride.id]), data)
        self.assertEqual(response.status_code, 403)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_data['message'], 'You are not authorized to update this ride.')