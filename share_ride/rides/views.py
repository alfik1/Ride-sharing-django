from rest_framework import  permissions
from rest_framework.generics import CreateAPIView,RetrieveAPIView,ListAPIView
from .models import Ride
from .serializers import *
from rest_framework.exceptions import PermissionDenied, APIException
from helpers.common import error_response,success_response
from rest_framework import status
from rest_framework.views import APIView
from .helper import convert_geocode_to_location, find_available_driver
from .tasks import simulate_ride_tracking

# Create Ride
class RideCreateView(CreateAPIView):
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_profile = self.request.user.profile

        if user_profile.user_type == "driver":
            # Prevent drivers from creating ride requests
            raise PermissionDenied("Drivers are not allowed to request rides.")

        try:
            serializer.save(rider=user_profile)
        except Exception as e:
            # Raise a generic API exception if something else goes wrong
            raise APIException("Something went wrong while creating the ride.")


# Ride Details
class RideDetailView(RetrieveAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_object(self):
        ride_id = self.kwargs.get(self.lookup_field)
        try:
            return Ride.objects.get(id=ride_id)
        except Ride.DoesNotExist:
            raise APIException("Ride not found", code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise APIException("Something went wrong!", code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# List All Rides
class RideListView(ListAPIView):
    queryset = Ride.objects.all().order_by('-created_at')
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]


class DriverAcceptRideView(APIView):#to accept the ride request by driver
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Lists all available ride requests for drivers.
        """
        if request.user.profile.user_type != "driver":
            return error_response(
                error_message="Only drivers can view available rides.",
                status=status.HTTP_403_FORBIDDEN
            )

        available_rides = Ride.objects.filter(
            status="requested",
            driver__isnull=True
        ).order_by('-created_at')
        serializer = RideSerializer(available_rides, many=True)
        return success_response(
            success_message="Available ride requests retrieved.",
            data=serializer.data
        )
    
    def post(self, request):
        """
        Allows a driver to accept a ride request.
        """
        # Make sure the logged-in user is a driver
        if request.user.profile.user_type != "driver":
            return error_response(
                error_message="Only drivers can accept ride requests.",
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Validate the incoming data (we expect a ride_id)
            serializer = RideAcceptSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    errors=serializer.errors,
                    error_message="Invalid input",
                    status=status.HTTP_400_BAD_REQUEST
                )

            ride_id = serializer.validated_data['ride_id']

            # Try fetching the ride by ID
            ride = Ride.objects.get(id=ride_id)

            if ride.status != "requested":
                return error_response(
                    error_message="This ride is not available for acceptance.",
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If the ride is already assigned to a different driver, block it
            if ride.driver is not None and ride.driver != request.user.profile:
                return error_response(
                    error_message="This ride is already assigned to a different driver.",
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If the current driver already accepted this ride, no need to reassign
            if ride.driver == request.user.profile and ride.status == "accepted":
                return success_response(
                    success_message="You have already accepted this ride.",
                    data={
                        "ride_id": ride.id,
                        "driver_id": ride.driver.id,
                        "driver_name": ride.driver.full_name
                    }
                )

            # Prevent the driver from accepting multiple active rides
            engaged = Ride.objects.filter(
                driver=request.user.profile,
                status__in=["accepted", "started"]
            ).exists()
            if engaged:
                return error_response(
                    error_message="You are already assigned to an active ride.",
                    status=status.HTTP_400_BAD_REQUEST
                )

            # All checks passed: assign driver to the ride and mark it as accepted
            ride.driver = request.user.profile
            ride.status = "accepted"
            ride.save()

            return success_response(
                success_message="Ride accepted successfully.",
                data={
                    "ride_id": ride.id,
                    "driver_id": ride.driver.id,
                    "driver_name": ride.driver.full_name
                },
                status=status.HTTP_200_OK
            )

        except Ride.DoesNotExist:
            return error_response(
                error_message="Ride not found",
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return error_response(
                error_message="Something went wrong!",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class RideStatusUpdateView(APIView): #To update ongoing ride status
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
            print(ride.driver)

            if request.user.profile != ride.driver:
                return error_response(error_message="You are not authorized to update this ride.",status=status.HTTP_403_FORBIDDEN)

            serializer = RideStatusUpdateSerializer(ride, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return success_response(success_message="Ride status updated successfully", data=serializer.data, status=status.HTTP_200_OK)
            return error_response(error_message=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Ride.DoesNotExist:
            return error_response(error_message='Ride not found', status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return error_response(error_message="Something went wrong!", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RideTrackingUpdateView(APIView): #realtime location updating view
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
            # Restrict updates to the assigned driver
            if request.user.profile != ride.driver:
                return error_response(
                    error_message="Only the assigned driver can update ride location.",
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = RideLocationUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    error_message=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = serializer.validated_data
            lat, lon = data["current_latitude"], data["current_longitude"]
            location = convert_geocode_to_location(lat, lon) #to convert the geocodes to nameable locations

            ride.current_location = location
            ride.current_latitude = lat
            ride.current_longitude = lon
            ride.save()

            # Start simulation if ride is "started" and this is the first update
            if ride.status == "started" and not hasattr(ride, '_simulation_started'):
                simulate_ride_tracking.delay(ride_id)  # Run task asynchronously
                ride._simulation_started = True  # Flag to prevent restarting

            return success_response(
                success_message="Ride location updated.",
                data={
                    "current_location": location,
                    "current_latitude": lat,
                    "current_longitude": lon
                }
            )
        except Ride.DoesNotExist:
            return error_response(
                error_message="Ride not found",
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                error_message="Something went wrong!",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        
class MatchRideView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
        except Ride.DoesNotExist:
            return error_response(error_message="Ride not found.", status=status.HTTP_404_NOT_FOUND)

        if ride.status != "requested":
            return error_response(error_message="Ride already matched or in progress.", status=status.HTTP_400_BAD_REQUEST)
    
        driver = find_available_driver(ride)  # Pass ride for proximity
        if not driver:
            return error_response(error_message="No available drivers at the moment.", status=status.HTTP_400_BAD_REQUEST)

        # Assign driver but don’t accept yet
        ride.driver = driver
        ride.save()  

        data = {
            "ride_id": ride.id,
            "driver_id": driver.id,
            "driver_name": driver.full_name
        }
        return success_response(success_message="Driver matched successfully. waiting to accept.", data=data)